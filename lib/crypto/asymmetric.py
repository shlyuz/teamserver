import nacl.utils
import nacl.public
import ast


def generate_nonce():
    """
    Generate a random 24 byte nonce

    :return:
    """
    return nacl.utils.random(nacl.public.Box.NONCE_SIZE)


def generate_private_key():
    """
    Generate a private/public keypair
    :return:
    """
    return nacl.public.PrivateKey.generate()


def private_key_from_bytes(sk_string):
    """
    Used to convert bytes from a private key stored in the config to a private key object

    :param sk_string: the string from [crypto][private_key] stored in the config
    :return: a nacl.public.PrivateKey object
    """
    return nacl.public.PrivateKey(ast.literal_eval(sk_string))


def public_key_from_bytes(pk_string):
    """
    Used to convert bytes from a public key stored in the config to a public key object

    :param pk_string: the string from [xxxx][public_key] stored in the config
    :return: a nacl.public.PublicKey object
    """
    return nacl.public.PublicKey(ast.literal_eval(pk_string))


def prepare_box(secret_key, target_public_key):
    """
    Prepare a nacl.public.Box() object using the given keys

    :param secret_key: secret_key to use
    :param target_public_key: Public key to use
    :return:
    """
    return nacl.public.Box(secret_key, target_public_key)


def prepare_sealed_box(key):
    """
    Prepare a nacl.public.Box() object using the given key

    :param key: Key to use to interact with the box
    :return:
    """
    return nacl.public.SealedBox(key)


def encrypt(msg_box, message):
    """
    Encrypt a message given a message box and the message. Prepends the encrypted message with a 24 byte nonce

    :param msg_box:
    :param message:
    :return:
    """
    nonce = generate_nonce()
    if isinstance(msg_box, nacl.public.SealedBox):
        # This is a sealed_box, we won't send a nonce
        encrypted_message = msg_box.encrypt(message)
    else:
        encrypted_message = msg_box.encrypt(message, nonce)

    encrypted_message = nonce + encrypted_message
    return encrypted_message


def decrypt(msg_box, message):
    """
    Decrypt the received message, ignoring the first 24 bytes, as that's the nonce

    :param msg_box:
    :param message:
    :return:
    """
    return msg_box.decrypt(message[24:])