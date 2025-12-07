import string
from ai_recommender import AIRecommender

class CaesarCipher:
    def __init__(self, shift=0):
        self.shift = shift
        self.upper_alpha = string.ascii_uppercase
        self.lower_alpha = string.ascii_lowercase
        self.modulus = 26

    def _shift_char(self, char, shift_amount):
        if char in self.upper_alpha:
            idx = self.upper_alpha.index(char)
            return self.upper_alpha[(idx + shift_amount) % self.modulus]
        elif char in self.lower_alpha:
            idx = self.lower_alpha.index(char)
            return self.lower_alpha[(idx + shift_amount) % self.modulus]
        else:
            return char

    def encrypt(self, plaintext, key=None):
        shift = key if key is not None else self.shift
        return ''.join(self._shift_char(c, shift) for c in plaintext)

    def decrypt(self, ciphertext, key=None):
        shift = key if key is not None else self.shift
        return ''.join(self._shift_char(c, -shift) for c in ciphertext)


class CaesarAttacker:
    def __init__(self):
        self.cipher = CaesarCipher()
        self.ai = AIRecommender()

    def attack(self, ciphertext):
        candidates = []
        print(f"\n[AI] Analyzing 26 possible candidates for: '{ciphertext[:20]}...'")
        for key in range(26):
            decrypted_text = self.cipher.decrypt(ciphertext, key)
            analysis = self.ai.analyze(decrypted_text)
            candidates.append({
                "key": key,
                "plaintext": decrypted_text,
                "score": analysis['score'],
                "details": analysis
            })
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates
