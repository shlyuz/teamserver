import nacl.utils
import nacl.public


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


def prepare_box(secret_key, target_public_key):
    """
    Prepare a nacl.public.Box() object using the given keys

    :param secret_key: secret_key to use
    :param target_public_key: Public key to use
    :return:
    """
    return nacl.public.Box(secret_key, target_public_key)


def encrypt(msg_box, message):
    """
    Encrypt a message given a message box and the message. Prepends the encrypted message with a 24 byte nonce

    :param msg_box:
    :param message:
    :return:
    """
    nonce = generate_nonce()
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