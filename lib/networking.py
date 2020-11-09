import socket
import struct
import pickle
import binascii
import ast
import secrets

import lib.crypto.rc6
import lib.crypto.hex_encoding
import lib.crypto.xor
import lib.crypto.asymmetric


def connect_to_listening_post_socket(addr, port):
    """
    Creates our management socket to interact with the teamserver
    :param addr:
    :param port:
    :return:
    """
    management_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    management_channel.connect(addr, port)
    return management_channel


def send_management_frame(teamserver, data):
    slen = struct.pack('<I', len(data))
    teamserver.logging.log(f"Encoded data: {data}", level="debug", source="lib.networking")
    teamserver.teamserver.management_socket.sendall(slen + data)


def recv_management_frame(teamserver):
    try:
        chunk = teamserver.teamserver.management_socket.recv(4)
    except:
        return ("")

    if len(chunk) > 4:
        return ()

    slen = struct.unpack('<I', chunk)[0]
    chunk = teamserver.teamserver.management_socket.recv(slen)
    while len(chunk) < slen:
        chunk = chunk + teamserver.teamserver.management_socket.recv(slen - len(chunk))


def kill_management_socket(teamserver):
    teamserver.teamserver.management_socket.close()


def cook_transmit_frame(teamserver, data):
    """

    :param teamserver:
    :param data: encoded/encrypted data ready to transmit
    :return:
    """
    # frame looks like {"id": 1, "frame_data": "somearbitrarydata", "chunks": 1}

    # TODO: Dynamically generate the rc6 key, and put in asymmetric envelope
    # Symmetric Encryption Routine
    rc6_key = secrets.token_urlsafe(16)
    teamserver.logging.log(f"rc6 key: {rc6_key}", level="debug", source="lib.networking")
    transmit_data = lib.crypto.rc6.encrypt(rc6_key, data.encode('utf-8'))

    encrypted_frames = []
    for chunk_index in range(len(transmit_data)):
        frame_chunk = {"frame_id": chunk_index, "data": transmit_data[chunk_index],
                       "chunk_len": len(transmit_data)}
        encrypted_frames.append(frame_chunk)

    # Encoding routine
    hex_frames = binascii.hexlify(pickle.dumps(encrypted_frames))
    hex_frames = lib.crypto.hex_encoding.encode_hex(hex_frames)
    enveloped_frames = lib.crypto.xor.single_byte_xor(hex_frames,
                                                      teamserver.config.config['crypto']['xor_key'])

    enveloped_frames = lib.crypto.hex_encoding.encode_hex(binascii.hexlify(rc6_key.encode("utf-8"))) + enveloped_frames
    teamserver.logging.log(f"Unenveloped data: {enveloped_frames}", level="debug", source="lib.networking")

    # Asymmetric Encryption
    lp_pubkey = teamserver.listeners['teamserver_id'][
        'public_key']  # TODO: Figure out how to get 'listener_id' properly
    frame_box = lib.crypto.asymmetric.prepare_box(teamserver.config.config['crypto']['private_key'], lp_pubkey)
    transmit_frames = lib.crypto.asymmetric.encrypt(frame_box, enveloped_frames)

    teamserver.logging.log(f"Enveloped data: {transmit_frames}", level="debug", source="lib.networking")
    return transmit_frames
    # send_management_frame(teamserver.teamserver_management_socket, transmit_frames)


def uncook_transmit_frame(teamserver, frame):
    """

    :param teamserver:
    :param frame:
    :return:
    """

    # Asymmetric Encryption Routine
    lp_pubkey = teamserver.listeners['teamserver_id'][
        'public_key']  # TODO: Figure out how to get 'listener_id' properly
    frame_box = lib.crypto.asymmetric.prepare_box(teamserver.config.config['crypto']['private_key'], lp_pubkey)
    transmit_frame = lib.crypto.asymmetric.decrypt(frame_box, frame)

    # Decoding Routine
    rc6_key = binascii.unhexlify(lib.crypto.hex_encoding.decode_hex(transmit_frame[0:44])).decode("utf-8")
    teamserver.logging.log(f"rc6 key: {rc6_key}", level="debug", source="lib.networking")
    unxord_frame = lib.crypto.xor.single_byte_xor(transmit_frame,
                                                  teamserver.config.config['crypto']['xor_key'])
    unenc_frame = lib.crypto.hex_encoding.decode_hex(unxord_frame)
    del unxord_frame
    unsorted_recv_frame = pickle.loads(binascii.unhexlify(unenc_frame[44:]))
    del unenc_frame

    data_list = []
    sorted_frames = sorted(unsorted_recv_frame, key=lambda i: i['frame_id'])
    del unsorted_recv_frame
    for data_index in range(len(sorted_frames)):
        data_list.append(sorted_frames[data_index]['data'])

    # Symmetric decryption routine
    # TODO: Extract the rc6 key
    decrypted_data = lib.crypto.rc6.decrypt(rc6_key, data_list)
    teamserver.logging.log(f"Decrypted data: {decrypted_data}", level="debug", source="lib.networking")

    return decrypted_data
