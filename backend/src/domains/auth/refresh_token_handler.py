import hashlib

from pwdlib import PasswordHash


refresh_token_hasher = PasswordHash.recommended() #.recommended uses the latest recommended hashing algorithm.
		
def hash_token(raw_token: str) -> str:
    return refresh_token_hasher.hash(raw_token)

def verify_refresh_token(raw_token: str, token_hash: str) -> bool:
    return refresh_token_hasher.verify(raw_token, token_hash)

def get_refresh_token_fingerprint(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()