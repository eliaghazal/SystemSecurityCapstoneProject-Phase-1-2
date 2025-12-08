
from ai_recommender import AIRecommender

def test_seg():
    ai = AIRecommender()
    
    texts = [
        "thecatisrunningafterthemouse",
        "mynameisjames",
        "zpulthftlzthq" # The wrong permutation from debug output
    ]
    
    for t in texts:
        print(f"\nAnalyzing: '{t}'")
        res = ai.analyze(t)
        print(f"Score: {res['score']}")
        print(f"Segmented: {res['segmented']}")
        if res['segmented']:
             # analyze doesn't return the segmented string text in the dict, 
             # but we can infer it worked if segmented=True
             # Let's peek at _segment_text directly
             seg, score = ai._segment_text(t)
             print(f"Segmentation: '{seg}'")

if __name__ == "__main__":
    test_seg()
