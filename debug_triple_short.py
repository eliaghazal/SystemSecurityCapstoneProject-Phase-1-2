
from triple_lock import TripleLock
from transposition_cipher import TranspositionCipher
from ai_recommender import AIRecommender

def test_repro_full():
    print("--- TRIPLE LOCK FULL REPRO (SHORT TEXT) ---")
    plaintext = "mynameisjames"
    caesar_shift = 7
    trans_key = "BRAVE"
    
    # Encrypt
    tl = TripleLock()
    l1 = tl.caesar.encrypt(plaintext, caesar_shift)
    print(f"L1 (Caesar): {l1}")
    l2 = tl.trans.encrypt(l1, trans_key)
    print(f"L2 (Trans):  {l2}")
    
    # We skip RSA as user said RSA is correct. Input to Transposition attacker is l2.
    
    print("\n[DEBUG] Running Transposition Attacker on L2...")
    # NOTE: check_caesar=True is CRITICAL here
    trans_candidates = tl.trans_cracker.attack(l2, check_caesar=True)
    
    if not trans_candidates:
        print("FAILED: No candidates found.")
        return

    top = trans_candidates[0]
    print(f"Top Candidate: Key={top['key']} | Score={top['score']:.4f}")
    print(f"Decrypted L2 (Shifted Text): '{top['plaintext']}'")
    
    # Check if this matches L1
    if top['plaintext'] == l1:
        print(">> Transposition Step PASS")
    else:
        print(f">> Transposition Step FAIL. Expected '{l1}'")
        
    print("\n[DEBUG] Running Caesar on Transposition Output...")
    caesar_candidates = tl.caesar_cracker.attack(top['plaintext'])
    
    if caesar_candidates:
        best_c = caesar_candidates[0]
        print(f"Top Caesar: Key={best_c['key']} | Plain='{best_c['plaintext']}'")
        if best_c['plaintext'] == plaintext:
            print(">> Caesar Step PASS")
        else:
             print(">> Caesar Step FAIL")
    else:
        print(">> Caesar Step FAIL (No candidates)")

if __name__ == "__main__":
    test_repro_full()
