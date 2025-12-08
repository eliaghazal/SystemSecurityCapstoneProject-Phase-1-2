
from caesar_cipher import CaesarCipher, CaesarAttacker
from ai_recommender import AIRecommender

def test_caesar():
    print("--- CAESAR SHORT TEXT DEBUG ---")
    inputs = ["mynameisjames", "thelovewasfound"]
    shift = 7
    
    attacker = CaesarAttacker()
    ai = AIRecommender()
    
    for plain in inputs:
        print(f"\nOriginal: '{plain}'")
        
        # Encrypt
        cipher = CaesarCipher(shift).encrypt(plain)
        print(f"Encrypted (Shift {shift}): '{cipher}'")
        
        # Attack
        print("Attacking...")
        candidates = attacker.attack(cipher)
        
        print("Top 3 Candidates:")
        for i, c in enumerate(candidates[:3]):
            print(f"{i+1}. Key={c['key']} | Plain='{c['plaintext']}' | Score={c['score']:.4f}")
            # If checking segmentation inside analysis
            # We can manually trigger ai analysis on this text to see details
            analysis = ai.analyze(c['plaintext'])
            print(f"   Details: Segmented={analysis['segmented']}")
            if analysis['segmented']:
                 # Re-run segment to see what it looked like
                 seg, _ = ai._segment_text(c['plaintext'])
                 print(f"   Segmentation: '{seg}'")
                 
        # Check rank of correct key
        found = False
        for i, c in enumerate(candidates):
            if c['key'] == shift:
                print(f">> Correct Key ({shift}) is Rank #{i+1} with Score={c['score']:.4f}")
                found = True
                break
        if not found:
            print(">> Correct Key NOT found in candidates list??")

if __name__ == "__main__":
    test_caesar()
