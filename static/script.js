function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}

async function postData(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}

// --- CAESAR ---
async function caesarEncrypt() {
    const text = document.getElementById('caesar-input').value;
    const shift = document.getElementById('caesar-shift').value;
    const res = await postData('/api/caesar/encrypt', { text, shift });
    document.getElementById('caesar-output').innerText = res.result;
}

async function caesarDecrypt() {
    const text = document.getElementById('caesar-input').value;
    const shift = document.getElementById('caesar-shift').value;
    const res = await postData('/api/caesar/decrypt', { text, shift });
    document.getElementById('caesar-output').innerText = res.result;
}

async function caesarAttack() {
    const text = document.getElementById('caesar-input').value;
    document.getElementById('caesar-output').innerText = "Attacking... please wait.";
    const res = await postData('/api/caesar/attack', { text });

    let html = "<h3>Top Recommendations:</h3>";
    res.results.forEach(r => {
        html += `<div class="result-item">
            <span class="result-score">${(r.score * 100).toFixed(1)}% Match</span> | Key: ${r.key}<br>
            ${r.plaintext}
        </div>`;
    });
    document.getElementById('caesar-output').innerHTML = html;
}

// --- TRANSPOSITION ---
async function transEncrypt() {
    const text = document.getElementById('trans-input').value;
    const key = document.getElementById('trans-key').value;
    const res = await postData('/api/transposition/encrypt', { text, key });
    document.getElementById('trans-output').innerText = res.result;
}

async function transDecrypt() {
    const text = document.getElementById('trans-input').value;
    const key = document.getElementById('trans-key').value;
    const res = await postData('/api/transposition/decrypt', { text, key });
    document.getElementById('trans-output').innerText = res.result;
}

async function transAttack() {
    const text = document.getElementById('trans-input').value;
    document.getElementById('trans-output').innerText = "Attacking... please wait.";
    const res = await postData('/api/transposition/attack', { text });

    let html = "<h3>Top Recommendations:</h3>";
    res.results.forEach(r => {
        html += `<div class="result-item">
            <span class="result-score">${(r.score * 100).toFixed(1)}% Match</span> | Key: ${r.key}<br>
            ${r.plaintext}
        </div>`;
    });
    document.getElementById('trans-output').innerHTML = html;
}

// --- RSA ---
async function rsaGenerate() {
    const res = await postData('/api/rsa/generate', {});
    document.getElementById('pub-key').innerText = `(${res.public[0]}, ${res.public[1]})`;
    document.getElementById('priv-key').innerText = `(${res.private[0]}, ${res.private[1]})`;

    // Auto-fill inputs
    document.getElementById('rsa-e').value = res.public[0];
    document.getElementById('rsa-n').value = res.public[1];
    document.getElementById('rsa-d').value = res.private[0];
}

async function rsaEncrypt() {
    const text = document.getElementById('rsa-input').value;
    const e = document.getElementById('rsa-e').value;
    const n = document.getElementById('rsa-n').value;

    const res = await postData('/api/rsa/encrypt', { text, e, n });
    if (res.error) {
        document.getElementById('rsa-output').innerText = "Error: " + res.error;
    } else {
        document.getElementById('rsa-output').innerText = res.result;
    }
}

async function rsaDecrypt() {
    const text = document.getElementById('rsa-input').value;
    const d = document.getElementById('rsa-d').value;
    const n = document.getElementById('rsa-n').value;

    const res = await postData('/api/rsa/decrypt', { text, d, n });
    if (res.error) {
        document.getElementById('rsa-output').innerText = "Error: " + res.error;
    } else {
        document.getElementById('rsa-output').innerText = res.result;
    }
}

async function rsaAttack() {
    const text = document.getElementById('rsa-input').value;
    const e = document.getElementById('rsa-e').value;
    const n = document.getElementById('rsa-n').value;

    document.getElementById('rsa-output').innerText = "Attacking... Factorizing n...";

    const res = await postData('/api/rsa/attack', { text, e, n });
    if (res.error) {
        document.getElementById('rsa-output').innerText = "Error: " + res.error;
    } else {
        document.getElementById('rsa-output').innerHTML = `
            <h3 style="color: var(--success)">Success!</h3>
            <p><strong>Recovered Private Key:</strong> (${res.private_key[0]}, ${res.private_key[1]})</p>
            <p><strong>Decrypted Message:</strong> ${res.decrypted}</p>
        `;
    }
}
