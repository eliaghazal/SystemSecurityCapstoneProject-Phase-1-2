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
        # TRIGRAMS are lowercase in knowledge base (count_3l.txt)
        clean_text = text.lower().replace(" ", "")
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
        
        # Map avg log prob to 0-1 scale
        # Correctly cased English trigrams typically measure around -2.0 to -3.0
        # Random text is usually < -6.0
        # Previous range [-15, -5] was for when we had case mismatches (smoothing only).
        # New Stricter Range: [-8.0, -2.5]
        normalized = max(0.0, min(1.0, (avg_score + 8.0) / 5.5))
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
            
            # Only correct if the word is NOT in our dictionary
            # AND it is in the spell_errors list
            if clean_w not in loader.unigrams and clean_w in loader.spell_errors:
                correct = loader.spell_errors[clean_w]
                # Preserve case/punctuation if possible (simple version)
                corrected_words.append(correct)
                corrections_made.append(f"{clean_w}->{correct}")
            else:
                corrected_words.append(w)
                
        return ' '.join(corrected_words), corrections_made

    def _segment_text(self, text):
        """
        Segments text into words using Viterbi algorithm.
        Returns: (segmented_text, score)
        """
        n = len(text)
        # dp[i] = max log prob of text[0:i]
        dp = [-float('inf')] * (n + 1)
        dp[0] = 0
        # path[i] = index of previous word boundary
        path = [-1] * (n + 1)
        
        for i in range(1, n + 1):
            # Try all possible previous word boundaries j
            # Limit word length to 20 for performance
            for j in range(max(0, i - 20), i):
                word = text[j:i]
                
                # Check if word exists in unigrams
                if word in loader.unigrams:
                    # Calculate score: dp[j] + log(P(word))
                    # We can use unigram probability here.
                    # Context (bigrams) is harder in simple Viterbi, but possible.
                    # For segmentation, unigram + length bonus is usually enough.
                    
                    count = loader.unigrams[word]
                    prob = count / loader.total_unigrams
                    log_prob = math.log10(prob)
                    
                    current_score = dp[j] + log_prob
                    
                    if current_score > dp[i]:
                        dp[i] = current_score
                        path[i] = j
                        
        # Reconstruct path
        if dp[n] == -float('inf'):
            return None, -float('inf')
            
        segments = []
        curr = n
        while curr > 0:
            prev = path[curr]
            segments.append(text[prev:curr])
            curr = prev
            
        return ' '.join(reversed(segments)), dp[n]

    def analyze(self, text):
        # Step A: Segmentation (Check for spaces)
        segmented_text = text
        was_segmented = False
        
        if " " not in text and len(text) > 10:
            # Try to segment
            seg, score = self._segment_text(text)
            if seg:
                segmented_text = seg
                was_segmented = True
            else:
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
        result = self.get_text_score(segmented_text)
        
        return {
            "score": result['score'],
            "log_prob": result['log_prob'],
            "details": result['details'],
            "segmented": was_segmented,
            "auto_correct": [] # Will be populated by attacker if needed
        }

    def analyze_substitution_potential(self, text):
        """
        Analyzes text to see if it *could* be English if Caesar shifted.
        Returns the best score found across all 26 shifts.
        """
        best_score = 0.0
        
        # We need a simple shift function here to avoid circular imports
        upper = string.ascii_uppercase
        lower = string.ascii_lowercase
        
        for shift in range(26):
            shifted = []
            for char in text:
                if char in upper:
                    idx = upper.index(char)
                    shifted.append(upper[(idx - shift) % 26])
                elif char in lower:
                    idx = lower.index(char)
                    shifted.append(lower[(idx - shift) % 26])
                else:
                    shifted.append(char)
            
            candidate = ''.join(shifted)
            
            # OPTIMIZATION:
            # Full 'analyze()' includes segmentation which is slow (O(N^2)).
            # Doing this for 45,000 permutations causes TIMEOUT.
            # We use a fast trigram check as a filter first.
            fast_score = self._get_char_trigram_score(candidate)
            
            if fast_score > 0.45:
                # Only if it looks promising, run the expensive full analysis
                # This catches "mynameisjames" (which has good trigrams too)
                res = self.analyze(candidate)
                # Take the BEST of either metric.
                # If dictionary is missing words (e.g. "meows"), segmentation score drops.
                # But trigram score remains high (0.8+). We should trust the high signal.
                score = max(fast_score, res['score'])
            else:
                score = fast_score
            
            if score > best_score:
                best_score = score
                
        return best_score
