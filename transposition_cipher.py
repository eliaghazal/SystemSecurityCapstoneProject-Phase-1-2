import math
import itertools
from ai_recommender import AIRecommender

class TranspositionCipher:
    """
    Implements Columnar Transposition Cipher.
    Treats spaces and punctuation as valid characters to be shuffled.
    """
    def _get_key_sequence(self, key):
        """
        Converts a keyword (str) or int into a numeric permutation sequence.
        Example: "ZEBRA" -> [4, 1, 0, 3, 2] (Indices of letters in alphabetical order)
        """
        if isinstance(key, int):
            # If key is an integer, assume it's just the column width
            # with standard 0,1,2... order (mostly for testing, less secure)
            return list(range(key))

        # If key is a string or list of numbers
        if isinstance(key, str):
            # Sort the characters and determine their original indices
            # e.g. "CAB" -> A(1), B(2), C(0) -> Sequence [1, 2, 0]
            # Standard method: Rank letters alphabetically
            # "ZEBRA" -> A(1), B(2), E(3), R(4), Z(5) -> ranks
            # We want the indices of the columns to read.
            # "ZEBRA":
            # Sorted: A(4), B(2), E(1), R(3), Z(0) -> [4, 2, 1, 3, 0]
            # This sequence means: Read column 4 first, then 2, then 1...
            key_indexed = sorted(list(enumerate(key)), key=lambda x: x[1])
            return [k[0] for k in key_indexed]

        return key # Assume it's already a list of ints

    def encrypt(self, plaintext, key):
        key_seq = self._get_key_sequence(key)
        num_cols = len(key_seq)

        # Build grid
        grid = [''] * num_cols
        for i, char in enumerate(plaintext):
            col_idx = i % num_cols
            grid[col_idx] += char

        # Read off columns in key_sequence order
        ciphertext = []
        for col_idx in key_seq:
            ciphertext.append(grid[col_idx])

        return ''.join(ciphertext)

    def decrypt(self, ciphertext, key):
        key_seq = self._get_key_sequence(key)
        num_cols = len(key_seq)
        num_rows = math.ceil(len(ciphertext) / num_cols)
        num_empty_cells = (num_rows * num_cols) - len(ciphertext)
        num_full_cells = num_cols - num_empty_cells

        # The grid is conceptually filled row by row.
        # But we receive it column by column.
        # We need to calculate how many characters belong to each column.
        # Columns 0 to (num_full_cells - 1) have 'num_rows' chars.
        # Columns num_full_cells to end have 'num_rows - 1' chars.

        col_lengths = [0] * num_cols
        for i in range(num_cols):
            if i < num_full_cells:
                col_lengths[i] = num_rows
            else:
                col_lengths[i] = num_rows - 1

        # Now split the ciphertext into columns based on the key sequence.
        # The ciphertext comes in the order of key_seq.

        cols_data = {}
        current_idx = 0

        for col_idx in key_seq:
            # How long is this specific column (in the original grid)?
            length = col_lengths[col_idx]
            # Extract that chunk
            cols_data[col_idx] = ciphertext[current_idx : current_idx + length]
            current_idx += length

        # Reconstruct the grid
        plaintext = []
        for r in range(num_rows):
            for c in range(num_cols):
                # Check if this cell exists (handle the short columns at end)
                if c >= num_full_cells and r == num_rows - 1:
                    continue # This cell was empty in the original grid

                # Append character if index exists
                if r < len(cols_data[c]):
                    plaintext.append(cols_data[c][r])

        return ''.join(plaintext)


class TranspositionAttacker:
    def __init__(self):
        self.cipher = TranspositionCipher()
        self.ai = AIRecommender()
        self.MAX_KEY_LEN_BRUTE = 7 # 7! = 5040 checks

    def attack(self, ciphertext):
        """
        Attempts to brute force column orders for key lengths 2 to MAX.
        """
        candidates = []
        print(f"\n[AI] Generating permutations for key lengths 2-{self.MAX_KEY_LEN_BRUTE}...")

        # Iterate through possible key lengths
        for k_len in range(2, self.MAX_KEY_LEN_BRUTE + 1):
            perms = itertools.permutations(range(k_len))

            for p in perms:
                try:
                    decrypted_text = self.cipher.decrypt(ciphertext, list(p))
                    analysis = self.ai.analyze(decrypted_text)

                    # CHANGED: REMOVED HARD FILTER "if analysis['score'] > 0.3"
                    # We now save everything and sort later.

                    candidates.append({
                        "key": f"Len {k_len} | {list(p)}",
                        "plaintext": decrypted_text,
                        "score": analysis['score'],
                        "details": analysis
                    })
                except Exception:
                    continue

        # Sort desc
        candidates.sort(key=lambda x: x['score'], reverse=True)

        # Return only top 100 to keep UI clean, but having scanned ALL of them.
        return candidates[:100]
