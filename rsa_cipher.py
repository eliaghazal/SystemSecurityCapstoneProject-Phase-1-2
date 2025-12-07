import random
import math

class RSACipher:
    def __init__(self):
        pass

    def is_prime(self, n):
        """Check if a number is prime using a basic trial division."""
        if n <= 1: return False
        if n <= 3: return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def generate_prime(self, min_val, max_val):
        """Generate a random prime number in a range."""
        while True:
            num = random.randint(min_val, max_val)
            if self.is_prime(num):
                return num

    def gcd(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def mod_inverse(self, a, m):
        """Compute modular multiplicative inverse of a modulo m."""
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
        # Make x positive
        if x < 0:
            x += m0
        return x

    def generate_keys(self, min_val=100, max_val=300):
        """
        Generates RSA public and private keys.
        Returns: ((e, n), (d, n))
        """
        p = self.generate_prime(min_val, max_val)
        q = self.generate_prime(min_val, max_val)
        while p == q:
            q = self.generate_prime(min_val, max_val)

        n = p * q
        phi = (p - 1) * (q - 1)

        # Choose e such that 1 < e < phi and gcd(e, phi) = 1
        e = random.randint(3, phi - 1)
        while self.gcd(e, phi) != 1:
            e = random.randint(3, phi - 1)

        # Calculate d
        d = self.mod_inverse(e, phi)

        return ((e, n), (d, n))

    def encrypt(self, plaintext, public_key):
        """
        Encrypts plaintext (string) using public_key (e, n).
        Converts chars to ASCII, then m^e mod n.
        Returns list of integers.
        """
        e, n = public_key
        cipher_ints = [pow(ord(char), e, n) for char in plaintext]
        return cipher_ints

    def decrypt(self, ciphertext, private_key):
        """
        Decrypts ciphertext (list of ints) using private_key (d, n).
        c^d mod n -> char.
        """
        d, n = private_key
        plain_chars = [chr(pow(char, d, n)) for char in ciphertext]
        return ''.join(plain_chars)


class RSAAttacker:
    def __init__(self):
        self.rsa = RSACipher()

    def attack(self, public_key):
        """
        Brute force attack on RSA by factorizing n.
        public_key: (e, n)
        Returns: private_key (d, n)
        """
        e, n = public_key
        print(f"\n[RSA Attack] Attempting to factorize n={n}...")

        # Brute force factorization
        # We know n = p * q. We just need to find one factor.
        # Since p and q are roughly sqrt(n), we search up to sqrt(n).
        p = None
        limit = int(math.isqrt(n)) + 1
        
        # Optimization: skip even numbers
        if n % 2 == 0:
            p = 2
        else:
            for i in range(3, limit, 2):
                if n % i == 0:
                    p = i
                    break
        
        if not p:
            print("[RSA Attack] Failed to factorize n (too large?).")
            return None

        q = n // p
        print(f"[RSA Attack] Factors found: p={p}, q={q}")

        phi = (p - 1) * (q - 1)
        d = self.rsa.mod_inverse(e, phi)
        
        print(f"[RSA Attack] Calculated private key: d={d}")
        return (d, n)
