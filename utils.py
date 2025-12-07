def print_separator():
    print("-" * 60)

def print_results(results):
    if not results:
        print("\n[AI] No likely candidates found.")
        return

    print_separator()
    top = results[0]
    confidence = top.get('confidence', 'N/A')
    
    print_separator()
    print(f"TOP RESULT | CONFIDENCE: {confidence}")
    print_separator()
    print(f"KEY: {top['key']}")
    print(f"TEXT: {top['plaintext']}")
    print(f"SCORE: {top['score']:.4f}")
    
    if 'corrections' in top and top['corrections']:
        print(f"AUTO-CORRECT: {', '.join(top['corrections'])}")
        
    print_separator()
    
    # Only show others if confidence is low or user might want to see them
    if confidence != "HIGH (MATCH FOUND)":
        print("Other Candidates:")
        limit = min(5, len(results))
        for i in range(1, limit):
            r = results[i]
            preview = r['plaintext'][:30].replace('\n', ' ')
            print(f"#{i+1} ({r['score']*100:.1f}%) {preview}...")
