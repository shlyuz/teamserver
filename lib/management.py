from threading import Thread
import asyncio
from lib import networking


def _get_cmd_sent_index(teamserver, cmd_txid):
    try:
        cmd_sent_index = next(index for (index, command) in enumerate(teamserver.cmd_sent) if command['txid'] == cmd_txid)
        return cmd_sent_index
    except StopIteration:
        teamserver.logging.log(f"Command {cmd_txid} not found!",
                               level="error", source="lib.listener")
    pass


def _get_cmd_queue_index(teamserver, cmd_txid):
    try:
        cmd_index = next(index for (index, command) in enumerate(teamserver.cmd_queue) if command['txid'] == cmd_txid)
        return cmd_index
    except StopIteration:
        teamserver.logging.log(f"Command {cmd_txid} not found!",
                               level="error", source="lib.listener")
    pass


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
