import random
import string
import hashlib

class URLGenerator:
    @staticmethod
    def generate_short_code(url: str, length: int = 6) -> str:
        """Generate a short url using B62 encoding"""
        chars = string.ascii_letters + string.digits

        # using hash
        hash_object = hashlib.md5(f"{url}{random.random()}".encode())
        hash_hex = hash_object.hexdigest()
        # convert to base 62
        num = int(hash_hex[:8], 16)
        res = ""

        while num > 0 and len(res) < length:
            res = chars[num % 62] + res
            num //= 62

        while len(res) < length:
            res = random.choice(chars) + res
    
        return res

    @staticmethod
    def is_valid_custom_code(code: str) -> bool:
        """Check if the custom code is valid"""
        if len(code) < 3 or len(code) > 20:
            return False
        allowed_chars = string.ascii_letters + string.digits + "-_"
        return all(c in allowed_chars for c in code)
        
    