import bcrypt
import base64
import hashlib
import hmac
from os import environ

def hash(input) -> str:
	msg = bytes(input, 'utf-16')

	return hmac.new(bytes(environ.get('MASTER_KEY'), 'utf-16'),
		msg,
		'md5').hexdigest()

def validate_hash(string, hashstring) -> bool:
	return hmac.compare_digest(hashstring, hash(string))

def hash_password(input) -> str:
	salt = bcrypt.gensalt()
	return bcrypt.hashpw(base64.b64encode(
			hashlib.sha256(input.encode('utf-8')).digest()),
			salt,
		).decode('utf-8')

def check_password(string, hashed) -> bool:
	return bcrypt.checkpw(base64.b64encode(hashlib.sha256(string.encode('utf-8')).digest()), hashed.encode('utf-8'))

BLOCKSIZE = 65536

def hash_file(path):

    hasher = hashlib.md5()

    with open(path, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)

    return hasher.hexdigest()
