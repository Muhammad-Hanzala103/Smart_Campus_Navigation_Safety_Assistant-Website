import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class EncryptionManager:
    def __init__(self, key=None):
        # In a real SaaS, this key would be derived from the University's Master Key
        # This is a sample key. In production, load from ENV or KMS.
        self.key = key or b'\xbf\xce\x1c\xef\x1b\x17\xe6\xcf\x7f\x8d\x8c\x8e\xbd\xbd\x8b\x8b\xbf\xce\x1c\xef\x1b\x17\xe6\xcf\x7f\x8d\x8c\x8e\xbd\xbd\x8b\x8b'

    def encrypt(self, plain_text):
        if not plain_text:
            return None
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plain_text.encode()) + padder.finalize()
        
        encrypted_text = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + encrypted_text).decode('utf-8')

    def decrypt(self, encrypted_text):
        if not encrypted_text:
            return None
        try:
            data = base64.b64decode(encrypted_text)
            iv = data[:16]
            encrypted_data = data[16:]
            
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
            
            return decrypted_data.decode('utf-8')
        except Exception as e:
            return "[Decryption Error]"

encryption_manager = EncryptionManager()
