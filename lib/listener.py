import asyncio
from threading import Thread

from lib import networking


def lp_init(frame, teamserver):
    reply_frame = {'cid': 1, "icount": 1, "t": "lpo", "tpk": b"\xDE\xAD\xF0\x0D"}
    return reply_frame


def lp_initalized(frame, teamserver):
    reply_frame = {'cid': 1, "icount": 1, "t": "lpmo", "tpk": b"\xDE\xAD\xF0\x0D"}
    return reply_frame


def lp_process_manifest(frame, teamserver):
    # TODO: Process the manifest
    reply_frame = lp_initalized(frame, teamserver)  # debug
    return reply_frame


def lp_rekey(frame, teamserver):
    reply_frame = lp_initalized(frame, teamserver)
    return reply_frame


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_management_socket(teamserver):
    teamserver = teamserver
    loop = asyncio.new_event_loop()
    teamserver.logging.log("Started Shlyuz teamserver listener socket", level="debug", source="teamserver_init")
    t = Thread(target=start_background_loop, args=(loop,), daemon=False)
    loop.create_task(asyncio.start_server(lambda reader, writer: networking.handle_client(reader=reader, writer=writer,
                                                                                          teamserver=teamserver),
                                          host=teamserver.config['l_addr'],
                                          port=int(teamserver.config['l_port']), ))
    t.start()
    return t
