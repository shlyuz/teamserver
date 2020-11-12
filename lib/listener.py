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
    data = {'component_id': frame['component_id'], "cmd": "lpo", "args": [{"tpk": teamserver.initial_public_key._public_key}],
            "txid": frame['txid']}
    instruction_frame = instructions.create_instruction_frame(data)
    # TODO: value setting
    reply_frame = instruction_frame  # Debug, will be encoded once cooked
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
    data = {'component_id': frame['component_id'], "cmd": "lpmo", "args": [{"tpk": teamserver.initial_public_key._public_key}],
            "txid": frame['txid']}
    # TODO: Value setting
    instruction_frame = instructions.create_instruction_frame(data)
    reply_frame = instruction_frame  # Debug, will be encoded once cooked
    teamserver.logging.log(f"Got new listening post! ID: {reply_frame['component_id']}", source="lib.listener")
    # f"Implants: {reply_frame['args']['implant_count']}", # TODO: list index must be int, not str

    return reply_frame


def lp_process_manifest(frame, teamserver):
    # TODO: Extract and process the manifest
    # TODO: Implement me
    listening_post_manifest = next(item for item in frame['args'] if item["component_id"] == frame['component_id'])
    listening_post_manifest['lpk'] = asymmetric.public_key_from_bytes(str(frame['args'][1]['lpk']))
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
    # TODO: implement me
    reply_frame = lp_initialized(frame, teamserver)
    return reply_frame



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
