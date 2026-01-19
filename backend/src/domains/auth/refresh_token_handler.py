from pwdlib import PasswordHash


refresh_token_hasher = PasswordHash.recommended() #.recommended uses the latest recommended hashing algorithm.
		
def hash_token(token: str) -> str:
    return refresh_token_hasher.hash(token)