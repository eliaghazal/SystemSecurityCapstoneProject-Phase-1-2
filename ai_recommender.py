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

    def get_text_score(self, text):
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
        
        # Smoothing
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
                prev_count = loader.unigrams.get(w_prev, 0)
                if prev_count == 0: prev_count = 1 
                
                p_bigram = bigram_count / prev_count
                log_prob += math.log10(p_bigram)
                details.append(f"P({w_curr}|{w_prev})={p_bigram:.2e}")
            else:
                # Backoff to Unigram P(curr)
                curr_count = loader.unigrams.get(w_curr, 0)
                p_unigram = (curr_count + 1) / (loader.total_unigrams + vocab_size)
                log_prob += math.log10(p_unigram)
                details.append(f"Backoff: P({w_curr})={p_unigram:.2e}")

        # Normalize
        avg_log_prob = log_prob / len(words)
        
        # Map avg log prob to 0-1 scale
        # Typical English avg log prob (base 10) is around -3 to -4.
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
        avg_score = score / (len(clean_text) - 2)
        # Map [-15, -5] to [0, 1]
        normalized = max(0.0, min(1.0, (avg_score + 15) / 10))
        return normalized

    def auto_correct(self, text):
        """
        Corrects common typos using the loaded spell_errors dictionary.
        """
        words = text.split()
        corrected_words = []
        corrections_made = []
        
        for w in words:
            # Check for punctuation
            clean_w = w.strip(string.punctuation).lower()
            
            if clean_w in loader.spell_errors:
                correct = loader.spell_errors[clean_w]
                # Preserve case/punctuation if possible (simple version)
                corrected_words.append(correct)
                corrections_made.append(f"{clean_w}->{correct}")
            else:
                corrected_words.append(w)
                
        return ' '.join(corrected_words), corrections_made

    def analyze(self, text):
        # Step A: Segmentation (Check for spaces)
        if " " not in text and len(text) > 10:
            # Step C: Ciphertext Fallback
            score = self._get_char_trigram_score(text)
            return {
                "score": score,
                "log_prob": 0,
                "details": ["Fallback to Character Trigrams"],
                "segmented": False,
                "auto_correct": []
            }
        
        # Step B: Scoring
        result = self.get_text_score(text)
        
        return {
            "score": result['score'],
            "log_prob": result['log_prob'],
            "details": result['details'],
            "segmented": True,
            "auto_correct": [] # Will be populated by attacker if needed
        }
