import random
import string

import lib.crypto.asymmetric
import lib.banner


def generate_private_key():
    return lib.crypto.asymmetric.generate_private_key()


banner = lib.banner.Banner()
rc6_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
xor_key = hex(random.randint(0, 255))
private_key = generate_private_key()

print(f"Put the following in your teamserver configuration:")
print(f"[crypto][private_key]: {private_key}")
print(f"[crypto][rc6_key]: {rc6_key}")
print(f"[crypto][xor_key]: {xor_key}")

print(f"\nListening Post Configuration values:")
print(f"[crypto][ts_pk]: {private_key.public_key}")
print(f"[crypto][sym_key]: {rc6_key}")
print(f"[crypto][xor_key]: {xor_key}")