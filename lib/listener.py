import asyncio
from threading import Thread

from lib import networking


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_management_socket(teamserver):
    teamserver = teamserver
    loop = asyncio.new_event_loop()
    teamserver.logging.log("Started Shlyuz teamserver listener socket", level="debug", source="teamserver_init")
    t = Thread(target=start_background_loop, args=(loop,), daemon=False)
    t.start()
    loop.create_task(loop.create_server(networking.handle_client, teamserver.config['l_addr'],
                                          int(teamserver.config['l_port'])))
