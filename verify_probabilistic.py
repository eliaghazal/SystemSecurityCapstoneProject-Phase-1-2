from ai_recommender import AIRecommender
from knowledge_base import loader

def test_loading():
    print("\n--- Testing Frequency Loader ---")
    print(f"Unigrams: {len(loader.unigrams)}")
    print(f"Bigrams (Top Words): {len(loader.bigrams)}")
    print(f"Trigrams: {len(loader.trigrams)}")
    
    assert len(loader.unigrams) > 0
    assert len(loader.bigrams) > 0
    assert len(loader.trigrams) > 0

def test_scoring():
    print("\n--- Testing Log-Prob Scoring ---")
    ai = AIRecommender()
    
    # Test 1: High probability sentence
    text1 = "the quick brown fox"
    res1 = ai.analyze(text1)
    print(f"Text: '{text1}' | Score: {res1['score']:.4f}")
    print(f"Details: {res1['details']}")
    
    # Test 2: Low probability sentence (nonsense)
    text2 = "the quick brown potato" # 'fox' is likely more common after 'brown' than 'potato'
    res2 = ai.analyze(text2)
    print(f"Text: '{text2}' | Score: {res2['score']:.4f}")
    print(f"Details: {res2['details']}")
    
    # Test 3: Gibberish
    text3 = "asdf jkl"
    res3 = ai.analyze(text3)
    print(f"Text: '{text3}' | Score: {res3['score']:.4f}")
    
    assert res1['score'] > res3['score']
    # res1 should ideally be > res2, but depends on bigram counts

def test_fallback():
    print("\n--- Testing Fallback (No Spaces) ---")
    ai = AIRecommender()
    text = "thequickbrownfox"
    res = ai.analyze(text)
    print(f"Text: '{text}' | Score: {res['score']:.4f}")
    assert res['score'] > 0.0
    assert res['segmented'] == False

if __name__ == "__main__":
    try:
        test_loading()
        test_scoring()
        test_fallback()
        print("\n[SUCCESS] Probabilistic Model verified!")
    except AssertionError as e:
        print("\n[FAILURE] Assertion failed.")
        raise e
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise e
