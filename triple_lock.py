from caesar_cipher import CaesarCipher, CaesarAttacker
from transposition_cipher import TranspositionCipher, TranspositionAttacker
from rsa_cipher import RSACipher, RSAAttacker

class TripleLock:
    def __init__(self):
        self.caesar = CaesarCipher()
        self.trans = TranspositionCipher()
        self.rsa = RSACipher()
        
        self.caesar_cracker = CaesarAttacker()
        self.trans_cracker = TranspositionAttacker()
        self.rsa_cracker = RSAAttacker()

    def encrypt(self, plaintext, caesar_shift, trans_key, rsa_pub_key):
        """
        Applies 3 layers of encryption:
        1. Caesar Cipher
        2. Transposition Cipher
        3. RSA Encryption
        """
        # Layer 1: Caesar
        layer1 = self.caesar.encrypt(plaintext, caesar_shift)
        
        # Layer 2: Transposition
        layer2 = self.trans.encrypt(layer1, trans_key)
        
        # Layer 3: RSA
        # RSA encrypt returns a list of integers
        layer3 = self.rsa.encrypt(layer2, rsa_pub_key)
        
        return layer3

    def attack(self, cipher_ints, rsa_pub_key):
        """
        Attacks the Triple Lock by peeling off layers:
        1. Crack RSA -> Scrambled Text
        2. Crack Transposition -> Shifted Text
        3. Crack Caesar -> Plaintext
        """
        results = {
            "rsa_decrypted": "Pending...",
            "trans_decrypted": "Pending...",
            "trans_score": 0.0,
            "final_plaintext": "Pending...",
            "success": False
        }
        
        # Step 1: RSA Attack
        print("[TripleLock] Breaking Layer 3: RSA...")
        rsa_result = self.rsa_cracker.attack(rsa_pub_key)
        
        if not rsa_result:
            results["rsa_decrypted"] = "FAILED: Could not factorize n."
            return results
            
        private_key = rsa_result['private_key']
        # Decrypt RSA layer
        scrambled_text = self.rsa.decrypt(cipher_ints, private_key)
        results["rsa_decrypted"] = scrambled_text
        
        # Step 2: Transposition Attack
        print("[TripleLock] Breaking Layer 2: Transposition...")
        # The output of RSA is the input to Transposition decryption
        trans_candidates = self.trans_cracker.attack(scrambled_text)
        
        if not trans_candidates:
            results["trans_decrypted"] = "FAILED: No transposition candidates found."
            return results
            
        # Take the top candidate
        best_trans = trans_candidates[0]
        shifted_text = best_trans['plaintext']
        results["trans_decrypted"] = f"{shifted_text} (Key: {best_trans['key']})"
        results["trans_score"] = best_trans['score']
        
        # Step 3: Caesar Attack
        print("[TripleLock] Breaking Layer 1: Caesar...")
        caesar_candidates = self.caesar_cracker.attack(shifted_text)
        
        if not caesar_candidates:
            results["final_plaintext"] = "FAILED: No Caesar candidates found."
            return results
            
        best_caesar = caesar_candidates[0]
        final_plaintext = best_caesar['plaintext']
        
        results["final_plaintext"] = f"{final_plaintext} (Key: {best_caesar['key']})"
        results["success"] = True
        
        return results
