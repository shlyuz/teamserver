import struct
import asyncio
import ast


async def handle_client(reader, writer):
    try:
        request_size = await reader.read(4)
        slen = struct.unpack('<I', request_size)[0]
        frame = await reader.read(slen)
        # TODO: Uncook request frame
        uncooked_frame = ast.literal_eval(frame.decode('utf-8'))  # DEBUG TODO:
        print(f"RCPT: {uncooked_frame}")
        if isinstance(uncooked_frame, dict):
            # TODO: Send uncooked_frame['t'] to a function that determines the type, then determine which queue to add it to, which internal manifest to update, make a response, etc
            #   This should generate a frame you need to cook, then put in the response
            reply_frame = {'cid': 1, "icount": 1, "t": "lpo", "tpk": b"\xDE\xAD\xF0\x0D"}
        # TODO: Do an await to get the response here, if any
        response = reply_frame # DEBUG TODO:
        print(f"SEND: {reply_frame}")
        rlen = struct.pack('<I', len(str(response).encode('utf-8')))
        # Send the response
        writer.write(rlen + str(response).encode('utf-8'))  # encode is debug, I think it'll already be there
        await writer.drain()
    except ConnectionResetError:
        writer.close()
    except Exception as e:
        print(f"Critical error when starting teamserver api server: {e}")
    writer.close()
