import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json

f = {'sep':'@','seq':['username','password','salt','domain']}

print(json.dumps(f))
