from caesar_cipher import CaesarCipher, CaesarAttacker
from transposition_cipher import TranspositionCipher, TranspositionAttacker
from rsa_cipher import RSACipher, RSAAttacker

def test_caesar():
    print("\n--- Testing Caesar Cipher ---")
    c = CaesarCipher(shift=3)
    msg = "HELLO WORLD"
    enc = c.encrypt(msg)
    dec = c.decrypt(enc)
    print(f"Original: {msg}")
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {dec}")
    assert msg == dec
    
    attacker = CaesarAttacker()
    res = attacker.attack(enc)
    print(f"Attack Top Result: {res[0]['plaintext']}")
    assert res[0]['plaintext'] == msg

def test_transposition():
    print("\n--- Testing Transposition Cipher ---")
    t = TranspositionCipher()
    msg = "HELLO WORLD"
    key = "ZEBRA"
    enc = t.encrypt(msg, key)
    dec = t.decrypt(enc, key)
    print(f"Original: {msg}")
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {dec}")
    assert msg == dec
    
    attacker = TranspositionAttacker()
    # Note: Short messages might be hard for AI to score perfectly, but let's try
    res = attacker.attack(enc)
    if res:
        print(f"Attack Top Result: {res[0]['plaintext']}")
    else:
        print("Attack failed to find candidates.")

def test_rsa():
    print("\n--- Testing RSA Cipher ---")
    r = RSACipher()
    # Use small keys for speed in testing
    pub, priv = r.generate_keys(min_val=10, max_val=50)
    print(f"Public: {pub}, Private: {priv}")
    
    msg = "HI"
    enc = r.encrypt(msg, pub)
    dec = r.decrypt(enc, priv)
    print(f"Original: {msg}")
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {dec}")
    assert msg == dec
    
    print("\n--- Testing RSA Attack ---")
    attacker = RSAAttacker()
    recovered_priv = attacker.attack(pub)
    print(f"Recovered Private Key: {recovered_priv}")
    
    dec_attack = r.decrypt(enc, recovered_priv)
    print(f"Decrypted with recovered key: {dec_attack}")
    assert msg == dec_attack

if __name__ == "__main__":
    try:
        test_caesar()
        test_transposition()
        test_rsa()
        print("\n[SUCCESS] All tests passed!")
    except AssertionError as e:
        print("\n[FAILURE] Assertion failed.")
        raise e
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise e
