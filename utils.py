def print_separator():
    print("-" * 60)

def print_results(results):
    if not results:
        print("\n[AI] No likely candidates found.")
        return

    print_separator()
    print("TOP AI RECOMMENDATIONS")
    print_separator()
    print(f"{'RANK':<5} {'CONFIDENCE':<12} {'KEY INFO':<20} {'TEXT'}")

    limit = min(5, len(results))
    for i in range(limit):
        r = results[i]
        # Clean up preview for display
        preview = r['plaintext'][:30].replace('\n', ' ')
        print(f"#{i+1:<4} {r['score']*100:>5.1f}%       {str(r['key'])[:18]:<20} {preview}...")

    top = results[0]
    print("\n[AI ANALYSIS]")
    print(f"Selected: {top['key']}")
    print(f"Dict Match: {top['details']['dict_score']*100:.1f}% | N-Gram: {top['details']['ngram_score']*100:.1f}%")
