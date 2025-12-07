import sys
import traceback
from caesar_cipher import CaesarCipher, CaesarAttacker
from transposition_cipher import TranspositionCipher, TranspositionAttacker
from rsa_cipher import RSACipher, RSAAttacker
from utils import print_separator, print_results

def main():
    try:
        # Initialize Ciphers
        caesar = CaesarCipher()
        caesar_cracker = CaesarAttacker()
        trans = TranspositionCipher()
        trans_cracker = TranspositionAttacker()
        rsa = RSACipher()
        rsa_cracker = RSAAttacker()

        # State for RSA Keys (to simulate a session)
        current_public_key = None
        current_private_key = None

        print_separator()
        print("      CRYPTO PROJECT: PHASE 1, 2 & 3")
        print("      (Caesar, Transposition, RSA)")
        print_separator()

        while True:
            print("\nMAIN MENU:")
            print("1. Caesar Cipher Tools")
            print("2. Transposition Cipher Tools")
            print("3. RSA Cipher Tools")
            print("4. Exit")

            main_choice = input("Select Cipher (1-4): ").strip()

            if main_choice == '1':
                # --- CAESAR SUBMENU ---
                print("\n[Caesar Mode]")
                print("1. Encrypt")
                print("2. Decrypt (Known Key)")
                print("3. Attack (Unknown Key)")
                sub = input("Choice: ").strip()

                if sub == '1':
                    txt = input("Plaintext: ")
                    try:
                        k = int(input("Shift (0-25): "))
                        print(f"Result: {caesar.encrypt(txt, k)}")
                    except ValueError:
                        print("Invalid input. Key must be an integer.")
                elif sub == '2':
                    txt = input("Ciphertext: ")
                    try:
                        k = int(input("Shift (0-25): "))
                        print(f"Result: {caesar.decrypt(txt, k)}")
                    except ValueError:
                        print("Invalid input. Key must be an integer.")
                elif sub == '3':
                    txt = input("Ciphertext: ")
                    res = caesar_cracker.attack(txt)
                    print_results(res)

            elif main_choice == '2':
                # --- TRANSPOSITION SUBMENU ---
                print("\n[Transposition Mode]")
                print("1. Encrypt (Keyword)")
                print("2. Decrypt (Keyword)")
                print("3. Attack (Brute Force Permutations)")
                sub = input("Choice: ").strip()

                if sub == '1':
                    txt = input("Plaintext: ")
                    k = input("Keyword (e.g., ZEBRA): ").strip()
                    print(f"Result: {trans.encrypt(txt, k)}")
                elif sub == '2':
                    txt = input("Ciphertext: ")
                    k = input("Keyword (e.g., ZEBRA): ").strip()
                    print(f"Result: {trans.decrypt(txt, k)}")
                elif sub == '3':
                    txt = input("Ciphertext: ")
                    res = trans_cracker.attack(txt)
                    print_results(res)

            elif main_choice == '3':
                # --- RSA SUBMENU ---
                print("\n[RSA Mode]")
                print("1. Generate Keys")
                print("2. Encrypt (Public Key)")
                print("3. Decrypt (Private Key)")
                print("4. Attack (Brute Force Factorization)")
                sub = input("Choice: ").strip()

                if sub == '1':
                    print("Generating keys...")
                    pub, priv = rsa.generate_keys()
                    current_public_key = pub
                    current_private_key = priv
                    print(f"Public Key (e, n): {pub}")
                    print(f"Private Key (d, n): {priv}")
                    print("(Keys saved to current session)")

                elif sub == '2':
                    txt = input("Plaintext: ")
                    if current_public_key:
                        use_stored = input(f"Use stored public key {current_public_key}? (y/n): ").lower()
                        if use_stored == 'y':
                            e, n = current_public_key
                        else:
                            e = int(input("Enter e: "))
                            n = int(input("Enter n: "))
                    else:
                        e = int(input("Enter e: "))
                        n = int(input("Enter n: "))
                    
                    cipher_ints = rsa.encrypt(txt, (e, n))
                    print(f"Ciphertext (space-separated ints): {' '.join(map(str, cipher_ints))}")

                elif sub == '3':
                    cipher_str = input("Ciphertext (space-separated ints): ")
                    try:
                        cipher_ints = list(map(int, cipher_str.strip().split()))
                        
                        if current_private_key:
                            use_stored = input(f"Use stored private key {current_private_key}? (y/n): ").lower()
                            if use_stored == 'y':
                                d, n = current_private_key
                            else:
                                d = int(input("Enter d: "))
                                n = int(input("Enter n: "))
                        else:
                            d = int(input("Enter d: "))
                            n = int(input("Enter n: "))

                        print(f"Result: {rsa.decrypt(cipher_ints, (d, n))}")
                    except ValueError:
                        print("Invalid input. Ciphertext must be integers.")

                elif sub == '4':
                    print("To attack, you need the Public Key (e, n) and the Ciphertext.")
                    e = int(input("Enter e: "))
                    n = int(input("Enter n: "))
                    cipher_str = input("Ciphertext (space-separated ints): ")
                    
                    try:
                        cipher_ints = list(map(int, cipher_str.strip().split()))
                        
                        # 1. Recover Private Key
                        recovered_key = rsa_cracker.attack((e, n))
                        
                        if recovered_key:
                            # 2. Decrypt
                            decrypted = rsa.decrypt(cipher_ints, recovered_key)
                            print(f"\n[SUCCESS] Decrypted Message: {decrypted}")
                        else:
                            print("\n[FAILURE] Could not recover private key.")
                            
                    except ValueError:
                        print("Invalid input.")

            elif main_choice == '4':
                break
            else:
                print("Invalid choice.")

    except Exception:
        print("\nCRITICAL ERROR:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
