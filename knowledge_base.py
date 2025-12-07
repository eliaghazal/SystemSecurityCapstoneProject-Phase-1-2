import os

class FrequencyLoader:
    def __init__(self, base_path="/Users/eliaghazal/Desktop/Word Files"):
        self.base_path = base_path
        self.unigrams = {}
        self.total_unigrams = 0
        self.bigrams = {}
        self.trigrams = {}
        self.total_trigrams = 0
        self.top_words = set()

        self.load_unigrams()
        self.load_bigrams()
        self.load_trigrams()

    def load_unigrams(self):
        path = os.path.join(self.base_path, "count_1.txt")
        if not os.path.exists(path):
            print(f"[Warning] Unigram file not found: {path}")
            return

        print("Loading Unigrams...")
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
        print(f"Loaded {len(self.unigrams)} unigrams. Total count: {self.total_unigrams}")

    def load_bigrams(self):
        path = os.path.join(self.base_path, "count_2.txt")
        if not os.path.exists(path):
            print(f"[Warning] Bigram file not found: {path}")
            return

        print("Loading Bigrams (Optimized)...")
        count_loaded = 0
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
                            count_loaded += 1
        print(f"Loaded {count_loaded} bigrams for top 5000 words.")

    def load_trigrams(self):
        path = os.path.join(self.base_path, "count_3l.txt")
        if not os.path.exists(path):
            print(f"[Warning] Trigram file not found: {path}")
            return

        print("Loading Character Trigrams...")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    trigram, count = parts
                    count = int(count)
                    self.trigrams[trigram] = count
                    self.total_trigrams += count
        print(f"Loaded {len(self.trigrams)} character trigrams.")

# Global instance
loader = FrequencyLoader()
