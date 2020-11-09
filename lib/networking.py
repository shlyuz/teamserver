import socket
import struct
import pickle
import binascii
import ast

import lib.crypto.rc6
import lib.crypto.hex_encoding
import lib.crypto.xor


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

    transmit_data = lib.crypto.rc6.encrypt(teamserver.config.config['crypto']['rc6_key'], data.encode('utf-8'))

    encrypted_frames = []
    for chunk_index in range(len(transmit_data)):
        frame_chunk = {"frame_id": chunk_index, "data": transmit_data[chunk_index],
                       "chunk_len": len(transmit_data)}
        encrypted_frames.append(frame_chunk)

    hex_frames = binascii.hexlify(pickle.dumps(encrypted_frames))
    hex_frames = lib.crypto.hex_encoding.encode_hex(hex_frames)
    transmit_frames = lib.crypto.xor.single_byte_xor(hex_frames,
                                                     ast.literal_eval(teamserver.config.config['crypto']['xor_key']))
    teamserver.logging.log(f"Encoded data: {transmit_frames}", level="debug", source="lib.networking")
    return transmit_frames
    # send_management_frame(teamserver.teamserver_management_socket, transmit_frames)


def uncook_transmit_frame(teamserver, frame):
    """

    :param teamserver:
    :param frame:
    :return:
    """
    # frame = recv_managmeent_frame(teamserver.teamserver_management_socket)
    unxord_frame = lib.crypto.xor.single_byte_xor(frame,
                                                  ast.literal_eval(teamserver.config.config['crypto']['xor_key']))
    unenc_frame = lib.crypto.hex_encoding.decode_hex(unxord_frame)
    del unxord_frame
    unsorted_recv_frame = pickle.loads(binascii.unhexlify(unenc_frame))
    del unenc_frame

    data_list = []
    sorted_frames = sorted(unsorted_recv_frame, key=lambda i: i['frame_id'])
    del unsorted_recv_frame
    for data_index in range(len(sorted_frames)):
        data_list.append(sorted_frames[data_index]['data'])

    decrypted_data = lib.crypto.rc6.decrypt(teamserver.config.config['crypto']['rc6_key'], data_list)
    teamserver.logging.log(f"Decrypted data: {decrypted_data}", level="debug", source="lib.networking")

    return decrypted_data