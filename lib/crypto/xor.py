def single_byte_xor(text, key):
    return bytes([b ^ key for b in text])
