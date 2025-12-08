from transposition_cipher import TranspositionCipher, TranspositionAttacker
from ai_recommender import AIRecommender

def test_robustness():
    cipher = TranspositionCipher()
    cracker = TranspositionAttacker()
    
    test_cases = [
        ("thecatsat", "Short combined"),
        ("fruitsaregoodforyou", "Medium combined"),
        ("defendtheeastwallofthecastle", "Long combined"),
        ("TheQuickBrownFoxJumpsOverTheLazyDog", "Mixed case combined"),
        ("sphinxofblackquartzjudgemyvow", "Pangram / Rare words"),
        ("securitysystemiscool", "Domain specific"),
    ]
    
    # Key to use
    key = "ZEBRA" # Len 5
    
    print(f"{'INPUT':<35} | {'RANK':<5} | {'SCORE':<7} | {'RESULT'}")
    print("-" * 75)
    
    for text, desc in test_cases:
        encrypted = cipher.encrypt(text, key)
        candidates = cracker.attack(encrypted)
        
        found_rank = -1
        found_score = 0.0
        
        # Normalize target for comparison
        target = text
        
        for i, cand in enumerate(candidates):
            # Check equality (case insensitive for fairness if needed, but exact match preferred)
            if cand['plaintext'] == target:
                found_rank = i + 1
                found_score = cand['score']
                break
        
        if found_rank == 1:
            status = "PASS"
        else:
            status = "FAIL" if found_rank == -1 else f"WARN (#{found_rank})"
            
        print(f"{text[:35]:<35} | #{found_rank:<4} | {found_score:.4f}  | {status}")
        
        if status != "PASS":
            print(f"   [!] Top 3 candidates for '{text[:15]}...':")
            for k in range(min(3, len(candidates))):
                c = candidates[k]
                print(f"      {k+1}. {c['plaintext']} (Score: {c['score']:.4f}) Key: {c['key']}")
                print(f"         Details: {c.get('details')}")

if __name__ == "__main__":
    test_robustness()
