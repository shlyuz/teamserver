import uuid
import time


def create_instruction_frame(data):
    # TODO: Map username to a guid, and embed it in the instruction frame for accounting
    instruction_frame = {
        "component_id": data['cid'],
        "command": data['cmd'],
        "args": data['args'],
        "transaction_id": uuid.uuid4().hex,
        "date": time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())
    }
    return instruction_frame