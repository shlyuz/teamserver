import struct
import asyncio
import ast

from lib import frame_orchestrator
from lib import transmit


async def handle_client(reader, writer, teamserver):
    teamserver.logging.log(f"TS Socket Conn: {reader._transport.get_extra_info('peername')}", level="debug",
                           source="lib.networking")
    try:
        request_size = await reader.read(4)
        if request_size == b'':
            raise ConnectionResetError
        slen = struct.unpack('<I', request_size)[0]
        frame = await reader.read(slen)
        if frame[:len(ast.literal_eval(teamserver.config['init_signature']))] == ast.literal_eval(teamserver.config['init_signature']):
            frame = frame[len(ast.literal_eval(teamserver.config['init_signature'])):]
            uncooked_frame = ast.literal_eval(transmit.uncook_sealed_frame(teamserver, frame).decode('utf-8'))
        else:
            uncooked_frame = ast.literal_eval(transmit.uncook_transmit_frame(teamserver, frame).decode('utf-8'))
        teamserver.logging.log(f"RCPT: {uncooked_frame}", level="debug", source="lib.networking")
        if isinstance(uncooked_frame, dict):
            reply_frame = frame_orchestrator.determine_destination(uncooked_frame, teamserver)
            if reply_frame is None:
                raise ConnectionResetError
        else:
            pass
        response = reply_frame
        teamserver.logging.log(f"SEND: {response}", level="debug", source="lib.networking")
        rlen = struct.pack('<I', len(str(response).encode('utf-8')))
        # Send the response
        writer.write(rlen + str(response).encode('utf-8'))  # encode is debug, I think it'll already be there
        await writer.drain()
    except ConnectionResetError:
        writer.close()
    except struct.error:
        teamserver.logging.log(f"Invalid Data", level="debug", source="lib.networking")
    except UnboundLocalError:
        teamserver.logging.log(f"Invalid frame received", level="error", source="lib.networking")
        teamserver.logging.log(f"Invalid frame {frame}", level="debug", source="lib.networking")
    except Exception as e:
        teamserver.logging.log(f"Encountered [{type(e).__name__}] {e}", level="error",
                               source="lib.networking")
    writer.close()
