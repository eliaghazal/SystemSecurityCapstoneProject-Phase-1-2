import string
from knowledge_base import COMMON_WORDS, COMMON_TRIGRAMS

class AIRecommender:
    def __init__(self):
        self.alpha = 0.7
        self.beta = 0.3

    def _clean_tokenize(self, text):
        if not text: return []
        translator = str.maketrans('', '', string.punctuation)
        clean_text = text.translate(translator).lower()
        return clean_text.split()

    def _get_dictionary_score(self, text):
        words = self._clean_tokenize(text)
        if not words:
            return 0.0
        matches = sum(1 for w in words if w in COMMON_WORDS)
        return matches / len(words)

    def _get_ngram_score(self, text):
        if not text: return 0.0
        clean_text = text.upper().replace(" ", "")

        if len(clean_text) < 3:
            return 0.0

        score = 0
        count = 0
        for i in range(len(clean_text) - 2):
            trigram = clean_text[i:i+3]
            if trigram in COMMON_TRIGRAMS:
                score += COMMON_TRIGRAMS[trigram]
            count += 1

        if count == 0: return 0.0
        return min(1.0, score / (count * 0.2))

    def _segment_text(self, text):
        """
        Splits a string without spaces into probable words using dynamic programming (Viterbi-like).
        Returns: (segmented_text, score)
        """
        n = len(text)
        # dp[i] = max score for substring text[0:i]
        dp = [-1.0] * (n + 1)
        dp[0] = 0.0
        # path[i] = index j < i that gave max score, to reconstruct path
        path = [-1] * (n + 1)

        for i in range(1, n + 1):
            for j in range(max(0, i - 20), i): # Look back up to 20 chars
                word = text[j:i]
                if word in COMMON_WORDS and dp[j] != -1.0:
                    # Score logic: longer words are better, but we sum them up
                    # Simple count of words found? Or length squared?
                    # Let's use length squared to prefer "information" over "in" + "formation"
                    current_score = dp[j] + (len(word) ** 2)
                    if current_score > dp[i]:
                        dp[i] = current_score
                        path[i] = j
        
        # Reconstruct
        if dp[n] == -1.0:
            return text, 0.0 # Failed to segment
        
        segments = []
        curr = n
        while curr > 0:
            prev = path[curr]
            segments.append(text[prev:curr])
            curr = prev
        
        return ' '.join(reversed(segments)), dp[n]

    def analyze(self, text):
        # 1. Standard Analysis
        dict_score = self._get_dictionary_score(text)
        ngram_score = self._get_ngram_score(text)

        # 2. No-Spacing Check
        # If dictionary score is low but text is long, it might be missing spaces.
        segmented_text = text
        was_segmented = False
        
        if dict_score < 0.2 and len(text) >= 8:
            # Try to segment
            seg_text, seg_score = self._segment_text(text.replace(" ", ""))
            if seg_score > 0:
                # Re-evaluate with segmented text
                seg_dict_score = self._get_dictionary_score(seg_text)
                if seg_dict_score > dict_score:
                    dict_score = seg_dict_score
                    # Recalculate ngram on segmented text? 
                    # Actually ngrams are usually robust to spaces, but let's keep original ngram score
                    # or maybe average them.
                    segmented_text = seg_text
                    was_segmented = True

        # Dynamic Weighting Logic:
        # If dictionary score is 0 (likely concatenated text), rely 100% on N-Grams.
        if dict_score == 0.0 and len(text) > 5:
            final_score = ngram_score # Ignore the 0 from dictionary
        else:
            final_score = (self.alpha * dict_score) + (self.beta * ngram_score)

        preview_text = segmented_text if segmented_text else "[Empty]"

        return {
            "score": final_score,
            "dict_score": dict_score,
            "ngram_score": ngram_score,
            "preview": preview_text[:60] + "..." if len(preview_text) > 60 else preview_text,
            "segmented": was_segmented
        }
