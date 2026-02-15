import hashlib

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended() #.recommended uses the latest recommended hashing algorithm.

def get_verification_token_fingerprint(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

def hash_verification_token(raw_token: str) -> str:
    return password_hash.hash(raw_token)

def verify_verification_token(raw_token: str, token_hash: str) -> bool:
    return password_hash.verify(raw_token, token_hash)
