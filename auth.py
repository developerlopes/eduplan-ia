import hashlib
import secrets
import re


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f'{salt}${digest}'


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split('$')
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest() == digest
    except Exception:
        return False


def valid_email(email: str) -> bool:
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email or '') is not None


def strong_password(password: str):
    if len(password or '') < 8:
        return False, 'A senha deve ter pelo menos 8 caracteres.'
    if not re.search(r'[A-Z]', password):
        return False, 'A senha deve conter pelo menos uma letra maiúscula.'
    if not re.search(r'[a-z]', password):
        return False, 'A senha deve conter pelo menos uma letra minúscula.'
    if not re.search(r'\d', password):
        return False, 'A senha deve conter pelo menos um número.'
    return True, ''


def generate_code() -> str:
    return str(secrets.randbelow(900000) + 100000)
