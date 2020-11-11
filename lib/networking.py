import struct
import asyncio
import ast

from lib import frame_orchestrator


async def handle_client(reader, writer, teamserver):
    teamserver.logging.log(f"TS Socket Conn: {reader._transport.get_extra_info('peername')}", level="debug",
                           source="lib.networking")
    try:
        request_size = await reader.read(4)
        if request_size == b'':
            raise ConnectionResetError
        slen = struct.unpack('<I', request_size)[0]
        frame = await reader.read(slen)
        # TODO: Uncook request frame
        uncooked_frame = ast.literal_eval(frame.decode('utf-8'))  # DEBUG TODO:
        teamserver.logging.log(f"RCPT: {uncooked_frame}", level="debug", source="lib.networking")
        if isinstance(uncooked_frame, dict):
            # TODO: Send uncooked_frame['t'] to a function that determines the type, then determine which queue to add it to, which internal manifest to update, make a response, etc
            #   This should generate a frame you need to cook, then put in the response
            reply_frame = frame_orchestrator.determine_destination(uncooked_frame, teamserver)
            if reply_frame is None:
                raise ConnectionResetError
        else:
            pass
        # TODO: Do an await to get the response here, if any
        response = reply_frame # DEBUG TODO:
        teamserver.logging.log(f"SEND: {reply_frame}", level="debug", source="lib.networking")
        rlen = struct.pack('<I', len(str(response).encode('utf-8')))
        # Send the response
        writer.write(rlen + str(response).encode('utf-8'))  # encode is debug, I think it'll already be there
        await writer.drain()
    except ConnectionResetError:
        writer.close()
    except struct.error:
        teamserver.logging.log(f"Invalid Data", level="debug", source="lib.networking")
    except Exception as e:
        teamserver.logging.log(f"Encountered [{type(e).__name__}] {e}", level="error",
                               source="lib.networking")
    writer.close()
