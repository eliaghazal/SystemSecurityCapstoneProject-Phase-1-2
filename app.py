from flask import Flask, render_template, request, jsonify
from caesar_cipher import CaesarCipher, CaesarAttacker
from transposition_cipher import TranspositionCipher, TranspositionAttacker
from rsa_cipher import RSACipher, RSAAttacker

app = Flask(__name__)

# Initialize Ciphers
caesar = CaesarCipher()
caesar_cracker = CaesarAttacker()
trans = TranspositionCipher()
trans_cracker = TranspositionAttacker()
rsa = RSACipher()
rsa_cracker = RSAAttacker()

# In-memory storage for RSA keys (per session simulation)
rsa_keys = {
    "public": None,
    "private": None
}

@app.route('/')
def index():
    return render_template('index.html')

# --- CAESAR ROUTES ---
@app.route('/api/caesar/encrypt', methods=['POST'])
def caesar_encrypt():
    data = request.json
    text = data.get('text')
    shift = int(data.get('shift', 0))
    result = caesar.encrypt(text, shift)
    return jsonify({'result': result})

@app.route('/api/caesar/decrypt', methods=['POST'])
def caesar_decrypt():
    data = request.json
    text = data.get('text')
    shift = int(data.get('shift', 0))
    result = caesar.decrypt(text, shift)
    return jsonify({'result': result})

@app.route('/api/caesar/attack', methods=['POST'])
def caesar_attack():
    data = request.json
    text = data.get('text')
    results = caesar_cracker.attack(text)
    return jsonify({'results': results[:5]}) # Return top 5

# --- TRANSPOSITION ROUTES ---
@app.route('/api/transposition/encrypt', methods=['POST'])
def trans_encrypt():
    data = request.json
    text = data.get('text')
    key = data.get('key')
    result = trans.encrypt(text, key)
    return jsonify({'result': result})

@app.route('/api/transposition/decrypt', methods=['POST'])
def trans_decrypt():
    data = request.json
    text = data.get('text')
    key = data.get('key')
    result = trans.decrypt(text, key)
    return jsonify({'result': result})

@app.route('/api/transposition/attack', methods=['POST'])
def trans_attack():
    data = request.json
    text = data.get('text')
    results = trans_cracker.attack(text)
    return jsonify({'results': results[:5]})

# --- RSA ROUTES ---
@app.route('/api/rsa/generate', methods=['POST'])
def rsa_generate():
    data = request.json
    strength = data.get('strength', 'strong')
    
    keysize = 1024
    if strength == 'weak':
        keysize = 32 # Small enough to brute force quickly
        
    pub, priv = rsa.generate_keys(keysize=keysize)
    rsa_keys['public'] = pub
    rsa_keys['private'] = priv
    
    # Convert to strings for JSON transport (prevent JS precision loss)
    pub_str = (str(pub[0]), str(pub[1]))
    priv_str = (str(priv[0]), str(priv[1]))
    return jsonify({'public': pub_str, 'private': priv_str})

@app.route('/api/rsa/encrypt', methods=['POST'])
def rsa_encrypt():
    data = request.json
    text = data.get('text')
    e = data.get('e')
    n = data.get('n')
    
    # Use stored keys if not provided
    if not e or not n:
        if rsa_keys['public']:
            e, n = rsa_keys['public']
        else:
            return jsonify({'error': 'No public key provided or generated'}), 400
            
    cipher_ints = rsa.encrypt(text, (int(e), int(n)))
    return jsonify({'result': ' '.join(map(str, cipher_ints))})

@app.route('/api/rsa/decrypt', methods=['POST'])
def rsa_decrypt():
    data = request.json
    text = data.get('text') # Space separated ints
    d = data.get('d')
    n = data.get('n')
    
    if not d or not n:
        if rsa_keys['private']:
            d, n = rsa_keys['private']
        else:
            return jsonify({'error': 'No private key provided or generated'}), 400
            
    try:
        cipher_ints = list(map(int, text.strip().split()))
        result = rsa.decrypt(cipher_ints, (int(d), int(n)))
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/rsa/attack', methods=['POST'])
def rsa_attack():
    data = request.json
    text = data.get('text') # Ciphertext ints
    e = int(data.get('e'))
    n = int(data.get('n'))
    
    try:
        cipher_ints = list(map(int, text.strip().split()))
        
        # 1. Recover Private Key
        attack_result = rsa_cracker.attack((e, n))
        
        if attack_result:
            recovered_key = attack_result['private_key']
            details = attack_result['details']
            
            # 2. Decrypt
            decrypted = rsa.decrypt(cipher_ints, recovered_key)
            return jsonify({
                'success': True,
                'private_key': recovered_key,
                'decrypted': decrypted,
                'details': details
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to factorize n'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- TRIPLE LOCK ROUTES ---
from triple_lock import TripleLock
triple_cipher = TripleLock()

@app.route('/api/triple/encrypt', methods=['POST'])
def triple_encrypt():
    data = request.json
    text = data.get('text')
    shift = int(data.get('shift'))
    trans_key = data.get('trans_key')
    e = int(data.get('e'))
    n = int(data.get('n'))
    
    cipher_ints = triple_cipher.encrypt(text, shift, trans_key, (e, n))
    return jsonify({'result': ' '.join(map(str, cipher_ints))})

@app.route('/api/triple/attack', methods=['POST'])
def triple_attack():
    data = request.json
    text = data.get('text') # Ciphertext ints
    e = int(data.get('e'))
    n = int(data.get('n'))
    
    try:
        # Sanitize input: Filter out any non-digit tokens (like "ENCRYPT", "LEVEL", etc.)
        tokens = text.strip().split()
        cipher_ints = [int(t) for t in tokens if t.isdigit()]
        
        if not cipher_ints:
            return jsonify({'error': 'No valid integer ciphertext found.'}), 400
            
        results = triple_cipher.attack(cipher_ints, (e, n))
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
