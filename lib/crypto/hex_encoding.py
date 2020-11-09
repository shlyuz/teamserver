def encode_hex(text):
    return text.replace(b'a', b'j').replace(b'c', b'n').replace(b'e', b'l').replace(b'f', b'g')


def decode_hex(text):
    return text.replace(b'j', b'a').replace(b'n', b'c').replace(b'l', b'e').replace(b'g', b'f')
