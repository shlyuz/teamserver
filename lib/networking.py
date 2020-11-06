import socket
import struct


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


def send_management_frame(sock, chunk):
    slen = struct.pack('<I', len(chunk))
    sock.sendall(slen + chunk)


def recv_management_frame(sock):
    try:
        chunk = sock.recv(4)
    except:
        return("")

    if len(chunk) > 4:
        return()

    slen = struct.unpack('<I', chunk)[0]
    chunk = sock.recv(slen)
    while len(chunk) < slen:
        chunk = chunk + sock.recv(slen - len(chunk))


def kill_management_socket(sock):
    sock.close()