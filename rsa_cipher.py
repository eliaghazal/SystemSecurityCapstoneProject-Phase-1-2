import random
import math

class RSACipher:
    def __init__(self):
        pass

    def gcd(self, a, b):
        while b != 0:
            a, b = b, a % b
        return a

    def mod_inverse(self, a, m):
        m0 = m
        y = 0
        x = 1
        if m == 1:
            return 0
        while a > 1:
            # q is quotient
            q = a // m
            t = m
            # m is remainder now, process same as Euclid's algo
            m = a % m
            a = t
            t = y
            # Update y and x
            y = x - q * y
            x = t
        if x < 0:
            x += m0
        return x

    def _is_prime_miller_rabin(self, n, k=40):
        """
        Miller-Rabin primality test.
        Returns True if n is (probably) prime, False if composite.
        """
        if n == 2 or n == 3: return True
        if n % 2 == 0 or n < 2: return False

        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    def generate_prime(self, bits):
        """Generates a prime number with approximately 'bits' bits."""
        while True:
            # Generate random odd number of 'bits' length
            n = random.getrandbits(bits)
            if n % 2 == 0: 
                n += 1
            
            # Ensure it's the right length (getrandbits can be smaller)
            mask = (1 << (bits - 1)) | 1
            n |= mask
            
            if self._is_prime_miller_rabin(n):
                return n

    def generate_keys(self, keysize=1024):
        """
        Generates RSA keys.
        keysize: Total bits for modulus n.
        Returns: ((e, n), (d, n))
        """
        # Generate p and q roughly half the size
        p = self.generate_prime(keysize // 2)
        q = self.generate_prime(keysize // 2)
        while p == q:
            q = self.generate_prime(keysize // 2)

        n = p * q
        phi = (p - 1) * (q - 1)

        # Choose e
        e = 65537 # Standard public exponent
        if self.gcd(e, phi) != 1:
            # Fallback if 65537 doesn't work (rare)
            e = random.randint(3, phi - 1)
            while self.gcd(e, phi) != 1:
                e = random.randint(3, phi - 1)

        d = self.mod_inverse(e, phi)
        return ((e, n), (d, n))

    def encrypt(self, plaintext, key):
        """
        Encrypts plaintext using key (e, n).
        Handles block encryption for long messages.
        Returns: List of integers (one per block).
        """
        e, n = key
        
        # Calculate max block size in bytes
        # n is roughly keysize bits.
        # We need block_int < n.
        # So block_size_bytes < n.bit_length() / 8
        key_bytes = (n.bit_length() + 7) // 8
        block_size = key_bytes - 1 # Safe margin
        
        if block_size < 1:
            # Fallback for tiny keys (e.g. 16-bit key -> n ~ 65000 -> 2 bytes)
            # block_size might be 1.
            block_size = 1

        # Convert plaintext to bytes
        message_bytes = plaintext.encode('utf-8')
        encrypted_blocks = []

        for i in range(0, len(message_bytes), block_size):
            block = message_bytes[i : i + block_size]
            # Convert block to int
            block_int = int.from_bytes(block, byteorder='big')
            # Encrypt
            cipher_int = pow(block_int, e, n)
            encrypted_blocks.append(cipher_int)

        return encrypted_blocks

    def decrypt(self, ciphertext, key):
        """
        Decrypts ciphertext (list of ints) using key (d, n).
        Returns: Decrypted string.
        """
        d, n = key
        
        # Calculate max block size for reconstruction
        key_bytes = (n.bit_length() + 7) // 8
        # Note: We don't strictly need block_size here for int_to_bytes 
        # if we just use the necessary length.
        
        decrypted_bytes = bytearray()
        
        for cipher_int in ciphertext:
            # Decrypt
            plain_int = pow(cipher_int, d, n)
            # Convert back to bytes
            # Length? It should be at most key_bytes - 1
            # But we can just use enough bytes to represent the int
            try:
                # We need to know how many bytes? 
                # int.to_bytes needs a length.
                # Use key_bytes as upper bound, then strip nulls?
                # Or just use (plain_int.bit_length() + 7) // 8?
                # Problem: Leading null bytes in the original block would be lost 
                # if we just use bit_length.
                # However, standard RSA padding (PKCS#1) handles this. 
                # Here we are doing "textbook RSA" with blocking.
                # If we assume the original block was full 'block_size' except the last one...
                # Simpler approach: use (plain_int.bit_length() + 7) // 8
                # This works if we don't have leading nulls in our utf-8 bytes (which is true for text)
                
                num_bytes = (plain_int.bit_length() + 7) // 8
                chunk = plain_int.to_bytes(num_bytes, byteorder='big')
                decrypted_bytes.extend(chunk)
            except Exception as e:
                print(f"[RSA Decrypt Error] {e}")
                continue

        return decrypted_bytes.decode('utf-8', errors='ignore')


class RSAAttacker:
    def __init__(self):
        self.rsa = RSACipher()

    def _pollards_rho(self, n):
        """
        Pollard's Rho algorithm for integer factorization.
        Good for finding small factors of composite numbers.
        """
        if n % 2 == 0: return 2
        
        x = random.randint(2, n - 1)
        y = x
        c = random.randint(1, n - 1)
        g = 1
        
        while g == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            g = self.rsa.gcd(abs(x - y), n)
            
            if g == n: # Failure, try different params
                return self._pollards_rho(n)
                
        return g

    def attack(self, public_key):
        """
        Attempts to recover private key from public key (e, n).
        Uses Trial Division for small n, Pollard's Rho for medium n.
        """
        e, n = public_key
        print(f"[RSA Attack] Attacking n={n} ({n.bit_length()} bits)...")
        
        p = None
        q = None
        
        # Strategy 1: Trial Division (Fast for < 32 bits)
        if n.bit_length() <= 32:
            print("[RSA Attack] Using Trial Division...")
            limit = int(math.isqrt(n)) + 1
            if n % 2 == 0:
                p = 2
            else:
                for i in range(3, limit, 2):
                    if n % i == 0:
                        p = i
                        break
        
        # Strategy 2: Pollard's Rho (Medium keys, e.g. < 64 bits)
        elif n.bit_length() <= 64:
            print("[RSA Attack] Using Pollard's Rho...")
            try:
                p = self._pollards_rho(n)
            except RecursionError:
                print("[RSA Attack] Pollard's Rho failed (recursion depth).")
        
        else:
            print("[RSA Attack] Key too large to crack in reasonable time (requires General Number Field Sieve).")
            return None

        if not p:
            print("[RSA Attack] Failed to find factors.")
            return None

        q = n // p
        print(f"[RSA Attack] Factors found: p={p}, q={q}")

        phi = (p - 1) * (q - 1)
        try:
            d = self.rsa.mod_inverse(e, phi)
            print(f"[RSA Attack] Calculated private key: d={d}")
            
            # Return details for GUI
            return {
                "private_key": (d, n),
                "details": {
                    "p": p,
                    "q": q,
                    "phi": phi,
                    "d": d
                }
            }
        except Exception as e:
            print(f"[RSA Attack] Error calculating d: {e}")
            return None
