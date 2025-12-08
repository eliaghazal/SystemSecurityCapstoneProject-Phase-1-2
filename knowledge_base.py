import os

class FrequencyLoader:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.unigrams = {}
        self.total_unigrams = 0
        self.bigrams = {}
        self.trigrams = {} # Char trigrams
        self.total_trigrams = 0
        self.quadgrams = {} # Char quadgrams
        self.total_quadgrams = 0
        self.char_bigrams = {} # Char bigrams
        self.total_char_bigrams = 0
        
        self.spell_errors = {}
        self.edit_dist_probs = {}
        
        self.top_words = set()

        # Load resources
        self.load_standard_resources()
        self.load_spelling_resources()

    def load_standard_resources(self, low_mem=False):
        # 1. Unigrams
        filename = "count_1w100k.txt" if low_mem else "count_1.txt"
        path = os.path.join(self.base_path, filename)
        
        if os.path.exists(path):
            print(f"Loading Unigrams from {filename}...")
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        word, count = parts
                        count = int(count)
                        self.unigrams[word] = count
                        self.total_unigrams += count
            
            # Identify top 5000 words for Bigram optimization
            sorted_words = sorted(self.unigrams.items(), key=lambda x: x[1], reverse=True)
            self.top_words = {w for w, c in sorted_words[:5000]}
        else:
            print(f"[Warning] Unigram file not found: {path}")

        # 2. Bigrams
        path = os.path.join(self.base_path, "count_2.txt")
        if os.path.exists(path):
            print("Loading Bigrams (Optimized)...")
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        words, count = parts
                        w_parts = words.split()
                        if len(w_parts) == 2:
                            w1, w2 = w_parts
                            # Optimization: Only load if w1 is in top 5000
                            if w1 in self.top_words:
                                if w1 not in self.bigrams:
                                    self.bigrams[w1] = {}
                                self.bigrams[w1][w2] = int(count)
        else:
            print(f"[Warning] Bigram file not found: {path}")

        # 3. Char Trigrams
        path = os.path.join(self.base_path, "count_3l.txt")
        if os.path.exists(path):
            print("Loading Character Trigrams...")
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        trigram, count = parts
                        count = int(count)
                        self.trigrams[trigram] = count
                        self.total_trigrams += count
        
        # 4. Char Bigrams
        path = os.path.join(self.base_path, "count_2l.txt")
        if os.path.exists(path):
            print("Loading Character Bigrams...")
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        bigram, count = parts
                        count = int(count)
                        self.char_bigrams[bigram] = count
                        self.char_bigrams[bigram] = count
                        self.total_char_bigrams += count

        # 5. Char Quadgrams (RECOMMENDED FOR TRANSPOSITION)
        path = os.path.join(self.base_path, "english_quadgrams.txt")
        if os.path.exists(path):
            print("Loading Character Quadgrams...")
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.strip().split() # Usually split by space
                    if len(parts) == 2:
                        quad, count = parts
                        count = int(count)
                        self.quadgrams[quad] = count
                        self.total_quadgrams += count
        else:
             print(f"[Warning] Quadgram file not found: {path} (Skipping Classical Scoring)")

    def load_spelling_resources(self):
        # 1. Spell Errors
        path = os.path.join(self.base_path, "spell_errors.txt")
        if os.path.exists(path):
            print("Loading Spell Errors...")
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Format: "correct: wrong1, wrong2"
                    if ":" in line:
                        correct, wrongs = line.split(":", 1)
                        correct = correct.strip()
                        for wrong in wrongs.split(","):
                            wrong = wrong.strip()
                            if wrong:
                                self.spell_errors[wrong] = correct
        
        # 2. Edit Distance Probs
        path = os.path.join(self.base_path, "count_edit.txt")
        if os.path.exists(path):
            print("Loading Edit Distance Probabilities...")
            # Format might vary, assuming simple key-value for now or just loading it
            # For this task, we might not strictly need the probabilities if we use the lookup table
            # But let's load it if we need sophisticated correction later.
            pass

# Global instance
loader = FrequencyLoader()
