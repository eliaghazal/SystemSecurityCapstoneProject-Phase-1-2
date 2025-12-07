from ai_recommender import AIRecommender
from caesar_cipher import CaesarAttacker, CaesarCipher
from transposition_cipher import TranspositionAttacker, TranspositionCipher

def test_full_system():
    print("\n--- Testing Full System with Probabilistic Model ---")
    
    # 1. Caesar Attack
    c_cipher = CaesarCipher(shift=7)
    c_plain = "the quick brown fox jumps over the lazy dog"
    c_enc = c_cipher.encrypt(c_plain)
    print(f"\n[Caesar] Encrypted: {c_enc}")
    
    c_attacker = CaesarAttacker()
    c_results = c_attacker.attack(c_enc)
    top_c = c_results[0]
    print(f"[Caesar] Top Result: {top_c['plaintext']} (Score: {top_c['score']:.4f})")
    assert top_c['plaintext'] == c_plain
    
    # 2. Transposition Attack
    t_cipher = TranspositionCipher()
    t_plain = "defend the east wall of the castle"
    t_key = [2, 0, 1] # Simple 3-col key
    t_enc = t_cipher.encrypt(t_plain, t_key)
    print(f"\n[Transposition] Encrypted: {t_enc}")
    
    t_attacker = TranspositionAttacker()
    t_results = t_attacker.attack(t_enc)
    top_t = t_results[0]
    print(f"[Transposition] Top Result: {top_t['plaintext']} (Score: {top_t['score']:.4f})")
    assert top_t['plaintext'] == t_plain

if __name__ == "__main__":
    try:
        test_full_system()
        print("\n[SUCCESS] Full system verified!")
    except AssertionError as e:
        print("\n[FAILURE] Assertion failed.")
        raise e
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise e
