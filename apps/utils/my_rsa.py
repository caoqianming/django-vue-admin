import base64
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher


def encrypt_data(msg, pub_key):
    pub_key = '-----BEGIN RSA PUBLIC KEY-----\n'+pub_key+'\n-----END RSA PUBLIC KEY-----'
    public_key = RSA.importKey(pub_key)
    cipher = PKCS1_cipher.new(public_key)
    encrypt_text = base64.b64encode(cipher.encrypt(bytes(msg.encode("utf8"))))
    return encrypt_text.decode('utf-8')
