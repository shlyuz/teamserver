import struct
import asyncio


async def handle_client(reader, writer):
    request_size = await reader.read(4)
    slen = struct.unpack('<I', request_size)[0]
    request = await reader.read(slen)
    # TODO: Do an await to get the response here, if any
    response = "blah"  # DEBUG TODO:
    rlen = struct.pack('<I', len(response))
    # Send the response
    writer.write(rlen + response.encode('utf-8'))  # encode is debug, I think it'll already be there
    await writer.drain()
    writer.close()
