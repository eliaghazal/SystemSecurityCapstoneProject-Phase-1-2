import math
import string
from knowledge_base import loader

class AIRecommender:
    def __init__(self):
        pass

    def _clean_tokenize(self, text):
        if not text: return []
        # Keep spaces for now to split, but remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        clean_text = text.translate(translator).lower()
        return clean_text.split()

    def get_log_probability(self, text):
        """
        Calculates the log-probability of the text using Unigrams and Bigrams.
        Returns: (log_prob_score, details)
        """
        words = self._clean_tokenize(text)
        if not words:
            return -float('inf'), {}

        log_prob = 0.0
        details = []
        
        # Step 1: First word (Unigram Probability)
        w1 = words[0]
        w1_count = loader.unigrams.get(w1, 0)
        
        # Smoothing for unigrams: add 1 to count, add vocab size to total
        # Simple Laplace smoothing for unknown words
        vocab_size = len(loader.unigrams)
        p_w1 = (w1_count + 1) / (loader.total_unigrams + vocab_size)
        log_prob += math.log10(p_w1)
        details.append(f"P({w1})={p_w1:.2e}")

        # Step 2: Subsequent words (Bigram Probability with Backoff)
        for i in range(1, len(words)):
            w_prev = words[i-1]
            w_curr = words[i]
            
            # Try Bigram P(curr | prev)
            bigram_count = 0
            if w_prev in loader.bigrams and w_curr in loader.bigrams[w_prev]:
                bigram_count = loader.bigrams[w_prev][w_curr]
            
            if bigram_count > 0:
                # P(curr | prev) = count(prev, curr) / count(prev)
                prev_count = loader.unigrams.get(w_prev, 0)
                # Avoid division by zero if prev not in unigrams (shouldn't happen if in bigrams)
                if prev_count == 0: prev_count = 1 
                
                p_bigram = bigram_count / prev_count
                log_prob += math.log10(p_bigram)
                details.append(f"P({w_curr}|{w_prev})={p_bigram:.2e}")
            else:
                # Backoff to Unigram P(curr)
                # Apply a penalty for backoff? Or just raw probability?
                # Usually backoff involves a weight alpha. For simplicity, we just use P(curr)
                curr_count = loader.unigrams.get(w_curr, 0)
                p_unigram = (curr_count + 1) / (loader.total_unigrams + vocab_size)
                log_prob += math.log10(p_unigram)
                details.append(f"Backoff: P({w_curr})={p_unigram:.2e}")

        # Normalize by length to compare texts of different lengths?
        # For ranking candidates of same length (Caesar), raw sum is fine.
        # For Transposition, length is constant.
        # But to give a 0-1 score for the GUI, we need normalization.
        # Average Log Prob per word
        avg_log_prob = log_prob / len(words)
        
        # Map avg log prob to 0-1 scale
        # Typical English avg log prob (base 10) is around -3 to -4.
        # Random text is much lower, e.g., -6 or -7.
        # Let's map [-7, -2] to [0, 1]
        normalized_score = max(0.0, min(1.0, (avg_log_prob + 7) / 5))

        return {
            "score": normalized_score,
            "log_prob": log_prob,
            "avg_log_prob": avg_log_prob,
            "details": details
        }

    def _get_char_trigram_score(self, text):
        """Fallback for text without spaces."""
        if not text: return 0.0
        clean_text = text.upper().replace(" ", "")
        if len(clean_text) < 3: return 0.0

        score = 0
        total_ngrams = loader.total_trigrams
        
        for i in range(len(clean_text) - 2):
            trigram = clean_text[i:i+3]
            count = loader.trigrams.get(trigram, 0)
            # Smoothing
            prob = (count + 1) / (total_ngrams + 26**3)
            score += math.log10(prob)
            
        # Normalize
        # Average log prob per trigram
        avg_score = score / (len(clean_text) - 2)
        print(f"DEBUG: Trigram Score: {score}, Avg: {avg_score}") # DEBUG
        
        # Typical English trigram log prob is around -3.5 to -4.5
        # But with large vocab, it might be lower.
        # Observed: -12.8
        # Map [-15, -5] to [0, 1]
        normalized = max(0.0, min(1.0, (avg_score + 15) / 10))
        return normalized

    def analyze(self, text):
        # Step A: Segmentation (Check for spaces)
        if " " not in text and len(text) > 10:
            # Step C: Ciphertext Fallback
            score = self._get_char_trigram_score(text)
            return {
                "score": score,
                "log_prob": 0,
                "details": ["Fallback to Character Trigrams"],
                "segmented": False
            }
        
        # Step B: Scoring
        result = self.get_log_probability(text)
        
        return {
            "score": result['score'],
            "log_prob": result['log_prob'],
            "details": result['details'], # List of probability steps
            "segmented": True,
            "matched_words": [], # Deprecated or can extract from details
            "top_ngrams": [] # Deprecated
        }
