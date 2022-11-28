from uuid import uuid4

def gen_id():
    return str(uuid4())[:8]