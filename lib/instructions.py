import uuid
import time


def create_instruction_frame(data):
    instruction_frame = {
        "component_id": data['component_id'],
        "cmd": data['cmd'],
        "args": data['args'],
        "date": time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())
    }
    if 'txid' not in data.keys():
        instruction_frame['txid'] = uuid.uuid4().hex
    else:
        instruction_frame['txid'] = data['txid']
    if 'uname' in data.keys():
        instruction_frame['uname'] = uuid.uuid4().hex
    return instruction_frame
