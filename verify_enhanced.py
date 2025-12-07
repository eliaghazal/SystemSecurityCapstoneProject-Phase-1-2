from ai_recommender import AIRecommender
from caesar_cipher import CaesarCipher, CaesarAttacker

def test_segmentation():
    print("\n--- Testing Word Segmentation ---")
    ai = AIRecommender()
    
    # Test 1: Simple concatenation
    text = "helloworld"
    res = ai.analyze(text)
    print(f"Input: '{text}' -> Preview: '{res['preview']}' | Score: {res['score']:.2f}")
    assert "hello world" in res['preview'] or res['score'] > 0.5
    
    # Test 2: Custom words
    text = "drcharbelisgreat"
    res = ai.analyze(text)
    print(f"Input: '{text}' -> Preview: '{res['preview']}' | Score: {res['score']:.2f}")
    # "dr" and "charbel" should be recognized
    assert res['score'] > 0.1

def test_caesar_no_space_attack():
    print("\n--- Testing Caesar Attack (No Spaces) ---")
    c = CaesarCipher(shift=5)
    attacker = CaesarAttacker()
    ai = AIRecommender() # Instantiate AI
    
    plaintext = "systemsecurityisimportant"
    ciphertext = c.encrypt(plaintext)
    print(f"Ciphertext: {ciphertext}")
    
    results = attacker.attack(ciphertext)
    
    # Debug: Print top 3
    print("\nTop 3 Candidates:")
    for i, r in enumerate(results[:3]):
        print(f"#{i+1}: Key={r['key']} | Score={r['score']:.4f} | Text={r['plaintext'][:30]}...")
        print(f"   Preview: {r['details']['preview']}")
        print(f"   Segmented: {r['details']['segmented']}")

    top = results[0]
    
    # Check score of expected
    expected_score = ai.analyze(plaintext)
    print(f"\nExpected Plaintext Score: {expected_score['score']:.4f}")
    print(f"Expected Preview: {expected_score['preview']}")

    assert top['plaintext'] == plaintext

if __name__ == "__main__":
    try:
        test_segmentation()
        test_caesar_no_space_attack()
        print("\n[SUCCESS] Enhanced features verified!")
    except AssertionError as e:
        print("\n[FAILURE] Assertion failed.")
        raise e
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise e
