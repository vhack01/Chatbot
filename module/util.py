import uuid


def generate_thread_id():
    return str(uuid.uuid4())


def generate_thread_title(message: str):
    return message[:10] + '...'