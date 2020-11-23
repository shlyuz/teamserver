from threading import Thread
import asyncio
from lib import networking


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_management_socket(teamserver):
    teamserver = teamserver
    loop = asyncio.new_event_loop()
    t = Thread(target=start_background_loop, args=(loop,), daemon=False)
    loop.create_task(asyncio.start_server(lambda reader, writer: networking.handle_client(reader=reader, writer=writer,
                                                                                          teamserver=teamserver),
                                          host=teamserver.config['l_addr'],
                                          port=int(teamserver.config['l_port']), ))
    t.start()
    return t
