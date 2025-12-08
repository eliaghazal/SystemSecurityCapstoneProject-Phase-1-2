from ai_recommender import AIRecommender
from knowledge_base import loader

def debug_scores():
    ai = AIRecommender()
    
    texts = ["cathestat", "thecatsat"]
    
    for text in texts:
        print(f"\nAnalyzing '{text}':")
        
        # 1. Segmentation
        seg, seg_score = ai._segment_text(text)
        print(f"  Segmentation: '{seg}' (Score: {seg_score:.2f})")
        
        # 2. Score Components
        hybrid, comps = ai.get_hybrid_score(text)
        print(f"  Hybrid: {hybrid:.4f}")
        print(f"    Word Match: {comps['word_match']:.4f}")
        print(f"    Quadgram: {comps['ngram']:.4f}")
        print(f"    Bigram: {comps['bigram']:.4f}")
        
        # 3. Word Validity Breakdown
        
        # 3. Word Validity Breakdown
        words = seg.split()
        for w in words:
            valid = "VALID"
            if w not in loader.unigrams: valid = "NOT IN DICT"
            else:
                clean = w.lower()
                safe_short = {'a','i','am','an','as','at','be','by','do','go','he','hi','if','in','is','it','me','my','no','of','oh','ok','on','or','so','to','up','us','we'}
                if len(clean) < 3 and clean not in safe_short: valid = "UNSAFE SHORT"
            
            print(f"    Word '{w}': {valid} (Count: {loader.unigrams.get(w, 0)})")
            
        # 4. Quadgram Breakdown
        print("    Quadgrams:")
        clean_text = text.upper()
        total_ngrams = loader.total_quadgrams
        running_score = 0
        for i in range(len(clean_text) - 3):
            quad = clean_text[i:i+4]
            count = loader.quadgrams.get(quad, 0)
            prob = (count + 1) / (total_ngrams + 26**4)
            import math
            s = math.log10(prob)
            running_score += s
            print(f"      {quad}: {count} (LogProb: {s:.2f})")
            
        avg = running_score / (len(clean_text) - 3)
        print(f"      Avg LogProb: {avg:.2f}")

if __name__ == "__main__":
    debug_scores()
