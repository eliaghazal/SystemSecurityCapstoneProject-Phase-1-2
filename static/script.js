function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}

// --- MATRIX BACKGROUND ---
const canvas = document.getElementById('matrix-bg');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const nums = '0123456789';
const alphabet = katakana + latin + nums;

const fontSize = 16;
const columns = canvas.width / fontSize;

const rainDrops = [];

for (let x = 0; x < columns; x++) {
    rainDrops[x] = 1;
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#0F0';
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < rainDrops.length; i++) {
        const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
        ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);

        if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            rainDrops[i] = 0;
        }
        rainDrops[i]++;
    }
}

setInterval(drawMatrix, 30);

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// --- HACKING EFFECT ---
function hackText(element, finalString, speed = 30) {
    const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()";
    let iterations = 0;

    const interval = setInterval(() => {
        element.innerText = finalString
            .split("")
            .map((letter, index) => {
                if (index < iterations) {
                    return finalString[index];
                }
                return letters[Math.floor(Math.random() * 26)];
            })
            .join("");

        if (iterations >= finalString.length) {
            clearInterval(interval);
        }

        iterations += 1 / 3;
    }, speed);
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
            <div class="result-header">
                <span class="result-score">${(r.score * 100).toFixed(1)}% Match</span> | Key: ${r.key}
            </div>
            <div class="result-text">${r.plaintext}</div>
            <div class="result-details">
                <p><strong>Log-Probability Analysis:</strong></p>
                <div class="log-details">
                    ${r.details.details.slice(0, 5).join('<br>')}
                    ${r.details.details.length > 5 ? '<br>...' : ''}
                </div>
                <p><small>Avg Log-Prob: ${r.details.log_prob ? (r.details.log_prob / r.plaintext.split(' ').length).toFixed(2) : 'N/A'}</small></p>
            </div>
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
            <div class="result-header">
                <span class="result-score">${(r.score * 100).toFixed(1)}% Match</span> | Key: ${r.key}
            </div>
            <div class="result-text">${r.plaintext}</div>
            <div class="result-details">
                <p><strong>Log-Probability Analysis:</strong></p>
                <div class="log-details">
                    ${r.details.details.slice(0, 5).join('<br>')}
                    ${r.details.details.length > 5 ? '<br>...' : ''}
                </div>
                <p><small>Avg Log-Prob: ${r.details.log_prob ? (r.details.log_prob / r.plaintext.split(' ').length).toFixed(2) : 'N/A'}</small></p>
            </div>
        </div>`;
    });
    document.getElementById('trans-output').innerHTML = html;
}

// --- RSA ---
async function rsaGenerate() {
    const isWeak = document.getElementById('rsa-weak-mode').checked;
    const strength = isWeak ? 'weak' : 'strong';

    const res = await postData('/api/rsa/generate', { strength });
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
            <div class="result-details">
                <p><strong>Factorization Details:</strong></p>
                <ul>
                    <li>n = ${n}</li>
                    <li>p = ${res.details.p}</li>
                    <li>q = ${res.details.q}</li>
                    <li>phi(n) = ${res.details.phi}</li>
                    <li>d = ${res.details.d} (Calculated via Modular Inverse)</li>
                </ul>
            </div>
        `;
    }
}

// --- TRIPLE LOCK ---
async function tripleEncrypt() {
    const text = document.getElementById('triple-input').value;
    const shift = document.getElementById('triple-shift').value;
    const trans_key = document.getElementById('triple-trans-key').value;
    const e = document.getElementById('triple-e').value;
    const n = document.getElementById('triple-n').value;

    const res = await postData('/api/triple/encrypt', { text, shift, trans_key, e, n });
    document.getElementById('triple-output').innerText = res.result;
}

async function tripleAttack() {
    const text = document.getElementById('triple-attack-input').value;
    const e = document.getElementById('triple-attack-e').value;
    const n = document.getElementById('triple-attack-n').value;

    const output = document.getElementById('triple-attack-output');
    output.innerHTML = "<span style='color: var(--danger)'>[SYSTEM] INITIATING DOOMSDAY DECRYPTION PROTOCOL...</span><br>";

    // Call API
    const res = await postData('/api/triple/attack', { text, e, n });

    if (res.error) {
        output.innerHTML += `<br><span style='color: red'>ERROR: ${res.error}</span>`;
        return;
    }

    const r = res.results;

    // Animation Sequence
    // 0s: RSA
    setTimeout(() => {
        output.innerHTML += "<br>[1/3] CRACKING RSA LAYER...<br>";
        if (r.step1_rsa.startsWith("FAILED")) {
            output.innerHTML += `<span style='color: red'>${r.step1_rsa}</span>`;
        } else {
            output.innerHTML += `<div class='result-text' style='color: #888;'>${r.step1_rsa}</div>`;
        }
    }, 100);

    // 2s: Transposition
    setTimeout(() => {
        output.innerHTML += "<br>[2/3] SOLVING TRANSPOSITION...<br>";
        if (r.step2_trans.startsWith("FAILED")) {
            output.innerHTML += `<span style='color: red'>${r.step2_trans}</span>`;
        } else {
            output.innerHTML += `<div class='result-text' style='color: #aaa;'>${r.step2_trans}</div>`;
        }
    }, 2000);

    // 4s: Caesar
    setTimeout(() => {
        output.innerHTML += "<br>[3/3] BREAKING CAESAR CIPHER...<br>";
    }, 4000);

    // 4.5s: Success
    setTimeout(() => {
        if (r.step3_caesar.startsWith("FAILED")) {
            output.innerHTML += `<span style='color: red'>${r.step3_caesar}</span>`;
        } else {
            output.innerHTML += `<br><span style='color: var(--success); font-size: 1.2rem; font-weight: bold;'>>> DECRYPTION SUCCESSFUL <<</span><br>`;
            output.innerHTML += `<div class='result-text' style='border: 2px solid var(--success); color: var(--success); font-size: 1.1rem;'>${r.final_plaintext}</div>`;
        }
    }, 4500);
}
