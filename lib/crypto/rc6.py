# Adapted from: https://asecuritysite.com/encryption/rc6
def rotate_right(x, n, bits=32):
    """
    # rotate right input x, by n bits
    """
    mask = (2 ** n) - 1
    mask_bits = x & mask
    return (x >> n) | (mask_bits << (bits - n))


def rotate_left(x, n, bits=32):
    """
    rotate left input x, by n bits
    """
    return rotate_right(x, bits - n, bits)


def block_converter(sentence):
    """
    convert input sentence into blocks of binary and creates 4 blocks of binary each of 32 bits.
    """
    encoded = []
    res = ""
    for i in range(0, len(sentence)):
        if i % 4 == 0 and i != 0:
            encoded.append(res)
            res = ""
        temp = bin(ord(sentence[i]))[2:]
        if len(temp) < 8:
            temp = "0" * (8 - len(temp)) + temp
        res = res + temp
    encoded.append(res)
    return encoded


def deblocker(blocks):
    """
    converts 4 blocks array of long int into string
    """
    s = ""
    for ele in blocks:
        temp = bin(ele)[2:]
        if len(temp) < 32:
            temp = "0" * (32 - len(temp)) + temp
        for i in range(0, 4):
            s = s + chr(int(temp[i * 8:(i + 1) * 8], 2))
    return s


def generate_key(user_key):
    """
    generate key s[0... 2r+3] from given input string user_key
    """
    r = 12
    w = 32
    b = len(user_key)
    modulo = 2 ** 32
    s = (2 * r + 4) * [0]
    s[0] = 0xB7E15163
    for i in range(1, 2 * r + 4):
        s[i] = (s[i - 1] + 0x9E3779B9) % (2 ** w)
    encoded = block_converter(user_key)
    # print encoded
    enlength = len(encoded)
    l = enlength * [0]
    for i in range(1, enlength + 1):
        l[enlength - i] = int(encoded[i - 1], 2)

    v = 3 * max(enlength, 2 * r + 4)
    A = B = i = j = 0

    for index in range(0, v):
        A = s[i] = rotate_left((s[i] + A + B) % modulo, 3, 32)
        B = l[j] = rotate_left((l[j] + A + B) % modulo, (A + B) % 32, 32)
        i = (i + 1) % (2 * r + 4)
        j = (j + 1) % enlength
    return s


def rc6_encrypt(sentence, s):
    encoded = block_converter(sentence)
    enlength = len(encoded)
    A = int(encoded[0], 2)
    B = int(encoded[1], 2)
    C = int(encoded[2], 2)
    D = int(encoded[3], 2)
    orgi = [A, B, C, D]
    r = 12
    w = 32
    modulo = 2 ** 32
    lgw = 5
    B = (B + s[0]) % modulo
    D = (D + s[1]) % modulo
    for i in range(1, r + 1):
        t_temp = (B * (2 * B + 1)) % modulo
        t = rotate_left(t_temp, lgw, 32)
        u_temp = (D * (2 * D + 1)) % modulo
        u = rotate_left(u_temp, lgw, 32)
        tmod = t % 32
        umod = u % 32
        A = (rotate_left(A ^ t, umod, 32) + s[2 * i]) % modulo
        C = (rotate_left(C ^ u, tmod, 32) + s[2 * i + 1]) % modulo
        (A, B, C, D) = (B, C, D, A)
    A = (A + s[2 * r + 2]) % modulo
    C = (C + s[2 * r + 3]) % modulo
    cipher = [A, B, C, D]
    return orgi, cipher


def rc6_decrypt(esentence, s):
    encoded = block_converter(esentence)
    enlength = len(encoded)
    A = int(encoded[0], 2)
    B = int(encoded[1], 2)
    C = int(encoded[2], 2)
    D = int(encoded[3], 2)
    cipher = [A, B, C, D]
    r = 12
    w = 32
    modulo = 2 ** 32
    lgw = 5
    C = (C - s[2 * r + 3]) % modulo
    A = (A - s[2 * r + 2]) % modulo
    for j in range(1, r + 1):
        i = r + 1 - j
        (A, B, C, D) = (D, A, B, C)
        u_temp = (D * (2 * D + 1)) % modulo
        u = rotate_left(u_temp, lgw, 32)
        t_temp = (B * (2 * B + 1)) % modulo
        t = rotate_left(t_temp, lgw, 32)
        tmod = t % 32
        umod = u % 32
        C = (rotate_right((C - s[2 * i + 1]) % modulo, tmod, 32) ^ u)
        A = (rotate_right((A - s[2 * i]) % modulo, umod, 32) ^ t)
    D = (D - s[1]) % modulo
    B = (B - s[0]) % modulo
    orgi = [A, B, C, D]
    return cipher, orgi


def encrypt(key, byte_data):
    # convert bytes to string for conversion
    byte_string = byte_data.decode("utf-8")

    chunk = [byte_string[i:i + 16] for i in range(0, len(byte_string), 16)]

    s = generate_key(key)

    # create list of chunks of length 16, encoded
    encrypted_string_chunks = []
    for byte_string in chunk:
        if len(byte_string) < 16:
            lenExtraChars = (16 - len(byte_string))
            byte_string = byte_string.ljust(16)
            encrypted_string_chunks.insert(0, lenExtraChars)

        orgi, cipher = rc6_encrypt(byte_string, s)
        ebyte_string = deblocker(cipher)
        encrypted_string_chunks.append(ebyte_string)

    return encrypted_string_chunks


def decrypt(key, encoded_data):
    s = generate_key(key)
    decrypted_string_chunks = []

    # check if characters had to be appended
    if isinstance(encoded_data[0], int):
        for encoded_byte_string in encoded_data[1:]:
            cipher, orgi = rc6_decrypt(encoded_byte_string, s)
            byte_string = deblocker(orgi)
            decrypted_string_chunks.append(byte_string)
    else:
        for encoded_byte_string in encoded_data:
            cipher, orgi = rc6_decrypt(encoded_byte_string, s)
            byte_string = deblocker(orgi)
            decrypted_string_chunks.append(byte_string)

    decrypted_chunks_joined = ''
    decrypted_chunks_joined = decrypted_chunks_joined.join(decrypted_string_chunks)

    decrypted_bytes = decrypted_chunks_joined.encode("utf-8")

    # remove appended characters if applicable
    if isinstance(encoded_data[0], int):
        decrypted_bytes = decrypted_bytes[:-encoded_data[0]]

    return decrypted_bytes
