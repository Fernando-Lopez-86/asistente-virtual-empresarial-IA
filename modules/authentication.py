from hashlib import sha256
from modules.database import get_user

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def login_user(username, password):
    user = get_user(username)
    if user and user[2] == hash_password(password):
        return user
    return None