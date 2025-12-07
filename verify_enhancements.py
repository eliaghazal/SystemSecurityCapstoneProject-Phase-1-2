from ai_recommender import AIRecommender
from rsa_cipher import RSAAttacker, RSACipher

def test_quadgrams():
    print("\n--- Testing Quadgram Loading ---")
    ai = AIRecommender()
    print(f"Total Quadgrams: {ai.total_quadgrams}")
    assert ai.total_quadgrams > 0
    
    # Test scoring
    text = "THEQUICKBROWNFOX"
    res = ai.analyze(text)
    print(f"Text: {text} | Score: {res['score']:.4f}")
    print(f"Top N-Grams: {res['top_ngrams']}")
    assert len(res['top_ngrams']) > 0

def test_rsa_details():
    print("\n--- Testing RSA Attack Details ---")
    rsa = RSACipher()
    attacker = RSAAttacker()
    
    # Generate small keys for fast testing
    pub, priv = rsa.generate_keys(min_val=50, max_val=200)
    e, n = pub
    print(f"Public Key: {pub}")
    
    result = attacker.attack(pub)
    details = result['details']
    
    print(f"Factorization: {n} = {details['p']} * {details['q']}")
    assert n == details['p'] * details['q']
    assert details['d'] == priv[0]

if __name__ == "__main__":
    try:
        test_quadgrams()
        test_rsa_details()
        print("\n[SUCCESS] Enhancements verified!")
    except AssertionError as e:
        print("\n[FAILURE] Assertion failed.")
        raise e
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise e
