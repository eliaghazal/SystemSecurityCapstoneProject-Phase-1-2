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
        # We must check for Caesar potential because the result is still Caesar encrypted!
        trans_candidates = self.trans_cracker.attack(scrambled_text, check_caesar=True)
        
        if not trans_candidates:
            results["trans_decrypted"] = "FAILED: No transposition candidates found."
            return results
            
        # NESTED ATTACK STRATEGY:
        # Instead of trusting the #1 transposition candidate blindly (which might be ranked #2 due to noise),
        # we take the TOP 5 candidates and try to crack Caesar on ALL of them.
        # We pick the winner based on the FINAL English score of the plaintext.
        
        best_overall_score = -1.0
        best_path = None
        
        # Check Top 5 (or fewer if less candidates)
        top_n = trans_candidates[:5]
        print(f"[TripleLock] Analyzing Top {len(top_n)} Transposition Paths...")
        
        for i, trans_cand in enumerate(top_n):
            shifted_text = trans_cand['plaintext']
            trans_key_disp = trans_cand['key']
            trans_score = trans_cand['score']
            
            # Run Caesar Attack on this candidate
            caesar_results = self.caesar_cracker.attack(shifted_text)
            
            if caesar_results:
                best_caesar_for_path = caesar_results[0]
                final_score = best_caesar_for_path['score']
                
                # Check if this path is the new best
                if final_score > best_overall_score:
                    best_overall_score = final_score
                    best_path = {
                        "trans_cand": trans_cand,
                        "caesar_cand": best_caesar_for_path
                    }
                    
        # Construct Final Result from Best Path
        if best_path:
            winning_trans = best_path['trans_cand']
            winning_caesar = best_path['caesar_cand']
            
            results["trans_decrypted"] = f"{winning_trans['plaintext']} (Key: {winning_trans['key']})"
            results["trans_score"] = winning_trans['score']
            results["trans_details"] = winning_trans['details']
            
            results["final_plaintext"] = f"{winning_caesar['plaintext']} (Key: {winning_caesar['key']})"
            results["caesar_details"] = winning_caesar['details']
            results["success"] = True
            
            print(f"[TripleLock] Winner Found! Score: {best_overall_score:.4f}")
        else:
            results["final_plaintext"] = "FAILED: No valid Caesar path found."
            
        return results
