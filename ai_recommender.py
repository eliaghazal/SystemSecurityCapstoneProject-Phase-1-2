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
                
                # PENALTY for Backoff:
                # Random permutations of words ("i ill a to") rely on backoff.
                # Valid sentences ("hello world") match bigrams.
                # We punish backoff to favor coherence.
                backoff_penalty = -1.0 # Divide prob by 10
                
                log_prob += math.log10(p_unigram) + backoff_penalty
                details.append(f"Backoff: P({w_curr})={p_unigram:.2e} (Penalty {backoff_penalty})")

        # Normalize Probability Score
        avg_log_prob = log_prob / len(words)
        prob_score = max(0.0, min(1.0, (avg_log_prob + 7) / 5))

        # 3. Content Density Score (IDF)
        # Prob score favors "to be or not to be" (common words).
        # We also want to favor "hello world" (specific content).
        # IDF = -log10(p). Rare words have high IDF. Unknown words have 0 IDF.
        total_idf = 0
        for w in words:
            if w in loader.unigrams:
                # Calculate p without smoothing for IDF lookup
                p = loader.unigrams[w] / loader.total_unigrams
                idf = -math.log10(p)
                total_idf += idf
        
        avg_idf = total_idf / len(words)
        # Normalize IDF: 
        # "the" ~ 1.0. "hello" ~ 4.5. "security" ~ 5.0. 
        # Map 0..5 to 0..1.
        content_score = min(1.0, avg_idf / 5.0)



        # 4. Dictionary Coverage Bonus
        # STRICT CHECK: 
        safe_short = {
            'a','i',
            'am','an','as','at','be','by','do','go','he','hi','if','in','is','it',
            'me','my','no','of','oh','ok','on','or','so','to','up','us','we'
        }
        
        def is_valid_word(w):
            if w not in loader.unigrams: return False
            if len(w) < 3 and w not in safe_short: return False
            return True

        in_dict_count = sum(1 for w in words if is_valid_word(w))
        coverage = in_dict_count / len(words) if words else 0
        
        # Scale bonus by word length
        avg_len = sum(len(w) for w in words) / len(words) if words else 0
        bonus_mult = 1.0
        if avg_len < 3.0: bonus_mult = 0.3
        
        coverage_bonus = 0.0
        if coverage == 1.0:
            coverage_bonus = 0.15 * bonus_mult
        elif coverage > 0.8:
            coverage_bonus = 0.05 * bonus_mult

        # 5. Final Weighted Score
        # Blend Fluency (Probability) and Content (IDF).
        # High Fluency + Low Content = "to be to be" (Mediocre)
        # High Fluency + High Content = "security breach" (Best)
        base_score = (prob_score * 0.4) + (content_score * 0.6)
        
        normalized_score = min(1.0, base_score + coverage_bonus)

        return {
            "score": normalized_score,
            "log_prob": log_prob,
            "avg_log_prob": avg_log_prob,
            "details": details + [f"IDF Score: {content_score:.2f} (Avg IDF {avg_idf:.1f})"]
        }

    def _get_char_trigram_score(self, text):
        """Deprecated: Kept for legacy compatibility if quadgrams missing."""
        if not text: return 0.0
        return self._get_quadgram_score(text)

    def _get_quadgram_score(self, text):
        """
        Method B: N-gram log-likelihood scoring (Quadgrams).
        Computes the log probability of the text based on English quadgram frequencies.
        """
        if not text: return 0.0
        # Quadgrams in file are typically UPPERCASE.
        clean_text = text.upper().replace(" ", "")
        if len(clean_text) < 4: return 0.0

        score = 0
        total_ngrams = loader.total_quadgrams
        if total_ngrams == 0: 
            # Fallback to trigrams if quadgrams not loaded
            return self._get_char_trigram_score_legacy(text)
            
        for i in range(len(clean_text) - 3):
            quad = clean_text[i:i+4]
            count = loader.quadgrams.get(quad, 0)
            # Smoothing (Add-1)
            prob = (count + 1) / (total_ngrams + 26**4)
            score += math.log10(prob)
            
        # Normalize by length to make it length-invariant
        avg_score = score / (len(clean_text) - 3)
        
        # Map avg log prob to 0-1 scale
        # English Text: approx -3.5 to -4.5
        # Random Text: approx -6.0 to -7.0
        # Range Mapping: [-6.5, -3.5] -> [0.0, 1.0]
        normalized = max(0.0, min(1.0, (avg_score + 6.5) / 3.0))
        return normalized

    def _get_char_trigram_score_legacy(self, text):
        """Fallback for text without spaces."""
        if not text: return 0.0
        clean_text = text.lower().replace(" ", "")
        if len(clean_text) < 3: return 0.0

        score = 0
        total_ngrams = loader.total_trigrams
        
        for i in range(len(clean_text) - 2):
            trigram = clean_text[i:i+3]
            count = loader.trigrams.get(trigram, 0)
            prob = (count + 1) / (total_ngrams + 26**3)
            score += math.log10(prob)
            
        avg_score = score / (len(clean_text) - 2)
        normalized = max(0.0, min(1.0, (avg_score + 8.0) / 5.5))
        return normalized

    def _get_word_match_score(self, text):
        """
        Method A: Dictionary / word-match scoring.
        Score = (# recognized words) / (total words)
        Uses segmentation to find words first.
        """
        # We rely on _segment_text or simple tokenization
        if " " not in text:
            # Try segmentation
            seg, _ = self._segment_text(text)
            if seg: text = seg
            else: return 0.0 # Failed to segment
            
        words = text.split()
        if not words: return 0.0
        
        # Count recognized words
        # 1. Standard Dictionary Check
        # 2. Length check (single letters other than 'a', 'i' are suspicious)
        recognized = 0
        total_len = 0
        
        safe_short = {'a','i','am','an','as','at','be','by','do','go','he','hi','if','in','is','it','me','my','no','of','oh','ok','on','or','so','to','up','us','we'}
        
        for w in words:
            clean_w = w.strip(string.punctuation).lower()
            if not clean_w: continue
            
            is_valid = False
            if clean_w in loader.unigrams:
                if len(clean_w) >= 3 or clean_w in safe_short:
                    is_valid = True
            
            if is_valid:
                recognized += 1
                
        return recognized / len(words)

    def get_hybrid_score(self, text):
        """
        Method D: Hybrid heuristic.
        final_score = α * word_match_score + β * ngram_score
        """
        # Component A
        word_match = self._get_word_match_score(text)
        
        # Component B
        ngram_score = self._get_quadgram_score(text)
        
        # Weights (Justification: N-gram is more robust for 'almost correctness', Word Match is precision)
        # For Transposition, we want robustness.
        alpha = 0.4
        beta = 0.6
        
        final_score = (alpha * word_match) + (beta * ngram_score)
        return final_score, {"word_match": word_match, "ngram": ngram_score}


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
        text = text.lower() # Fix case sensitivity for "Ilovesystemsecurity"
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
                # STRICT SEGMENTATION: 
                # Only allow verified short words (len < 3) to prevent garbage tiling.
                # Must match strict list: 'a', 'i', 'is', 'to', etc.
                is_safe_short = True
                if len(word) < 3:
                    safe_set = {
                        'a','i',
                        'am','an','as','at','be','by','do','go','he','hi','if','in','is','it',
                        'me','my','no','of','oh','ok','on','or','so','to','up','us','we'
                    }
                    if word not in safe_set:
                         is_safe_short = False
                
                if not is_safe_short:
                    continue
                    
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
        """
        Analyzes text using Hybrid Scoring (Method D).
        """
        # Step 1: Calculate Hybrid Score (A + B)
        score, components = self.get_hybrid_score(text)
        
        # Step 2: Details
        details = [
            f"Hybrid Score: {score:.4f}",
            f"  - Word Match (A): {components['word_match']:.4f}",
            f"  - Quadgram (B): {components['ngram']:.4f}"
        ]
        
        # Try to segment for display, but score comes from Hybrid
        segmented_text = text
        was_segmented = False
        if " " not in text:
            seg, _ = self._segment_text(text)
            if seg:
                segmented_text = seg
                was_segmented = True
        
        return {
            "score": score,
            "log_prob": 0, # Legacy
            "details": details,
            "segmented": was_segmented,
            "auto_correct": []
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
            # We use a fast Quadgram check as a filter first.
            fast_score = self._get_quadgram_score(candidate)
            
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
