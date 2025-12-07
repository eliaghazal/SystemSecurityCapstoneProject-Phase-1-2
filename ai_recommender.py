import string
from knowledge_base import COMMON_WORDS, COMMON_TRIGRAMS

import math
import os

class AIRecommender:
    def __init__(self):
        self.alpha = 0.6 # Weight for Dictionary
        self.beta = 0.4  # Weight for N-Grams
        self.quadgrams = {}
        self.total_quadgrams = 0
        self._load_quadgrams()

    def _load_quadgrams(self):
        filename = 'english_quadgrams.txt'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    key, count = line.split()
                    self.quadgrams[key] = int(count)
            self.total_quadgrams = sum(self.quadgrams.values())
        else:
            # Fallback to trigrams if file missing (though we downloaded it)
            pass

    def _clean_tokenize(self, text):
        if not text: return []
        translator = str.maketrans('', '', string.punctuation)
        clean_text = text.translate(translator).lower()
        return clean_text.split()

    def _get_dictionary_score(self, text):
        words = self._clean_tokenize(text)
        if not words:
            return 0.0, []
        matches = [w for w in words if w in COMMON_WORDS]
        score = len(matches) / len(words)
        return score, matches

    def _get_ngram_score(self, text):
        if not text: return 0.0, []
        clean_text = text.upper().replace(" ", "")
        if len(clean_text) < 4:
            return 0.0, []

        score = 0
        top_ngrams = []
        
        if self.quadgrams:
            # Log-likelihood scoring
            for i in range(len(clean_text) - 3):
                quad = clean_text[i:i+4]
                if quad in self.quadgrams:
                    prob = self.quadgrams[quad] / self.total_quadgrams
                    score += math.log10(prob)
                    top_ngrams.append(quad)
                else:
                    score += math.log10(0.01 / self.total_quadgrams) # Floor
            
            # Normalize log score roughly to 0-1 range for hybrid calc
            # Typical English quadgram log prob is around -4 per char
            # This is heuristic normalization
            expected = -4.0 * (len(clean_text) - 3)
            normalized_score = max(0, 1 - abs((score - expected) / expected))
            return normalized_score, top_ngrams[:5]
        else:
            # Fallback to Trigrams
            count = 0
            for i in range(len(clean_text) - 2):
                trigram = clean_text[i:i+3]
                if trigram in COMMON_TRIGRAMS:
                    score += COMMON_TRIGRAMS[trigram]
                    top_ngrams.append(trigram)
                count += 1
            if count == 0: return 0.0, []
            return min(1.0, score / (count * 0.2)), top_ngrams[:5]

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
        dict_score, matches = self._get_dictionary_score(text)
        ngram_score, top_ngrams = self._get_ngram_score(text)

        # 2. No-Spacing Check
        segmented_text = text
        was_segmented = False
        
        if dict_score < 0.2 and len(text) >= 8:
            # Try to segment
            seg_text, seg_score = self._segment_text(text.replace(" ", ""))
            if seg_score > 0:
                # Re-evaluate with segmented text
                seg_dict_score, seg_matches = self._get_dictionary_score(seg_text)
                if seg_dict_score > dict_score:
                    dict_score = seg_dict_score
                    matches = seg_matches
                    segmented_text = seg_text
                    was_segmented = True

        # Dynamic Weighting Logic
        if dict_score == 0.0 and len(text) > 5:
            final_score = ngram_score 
        else:
            final_score = (self.alpha * dict_score) + (self.beta * ngram_score)

        preview_text = segmented_text if segmented_text else "[Empty]"

        return {
            "score": final_score,
            "dict_score": dict_score,
            "ngram_score": ngram_score,
            "preview": preview_text[:60] + "..." if len(preview_text) > 60 else preview_text,
            "segmented": was_segmented,
            "matched_words": matches[:10], # Top 10 matches
            "top_ngrams": top_ngrams
        }
