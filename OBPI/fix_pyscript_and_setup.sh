#!/bin/bash

# --- 1. Patch index.html for latest PyScript ---
HTML="index.html"
if grep -q "pyscript.net" "$HTML"; then
    echo "[*] Updating PyScript CDN in $HTML..."
    # Replace old pyscript links with the latest
    sed -i 's|https://pyscript.net/[^"]\+core.js|https://pyscript.net/releases/2024.1.1/core.js|g' "$HTML"
    sed -i 's|https://pyscript.net/[^"]\+core.css|https://pyscript.net/releases/2024.1.1/core.css|g' "$HTML"
    sed -i 's|https://pyscript.net/[^"]\+pyscript.css|https://pyscript.net/releases/2024.1.1/core.css|g' "$HTML"
    sed -i 's|https://pyscript.net/[^"]\+pyscript.js|https://pyscript.net/releases/2024.1.1/core.js|g' "$HTML"
else
    echo "[*] Adding PyScript CDN to $HTML..."
    sed -i '/<head>/a \
<link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">\n\
<script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>' "$HTML"
fi

# --- 2. Patch index.html to auto-call pyscript.load() for dynamic <py-script> tags ---
if ! grep -q "window.pyscript.load()" "$HTML"; then
    echo "[*] Ensuring dynamic pyscript.load() call is present (add this to your JS for dynamic py-script tags):"
    echo 'After appending a <py-script> tag, call: if (window.pyscript && window.pyscript.load) window.pyscript.load();'
fi

# --- 3. Offer to start a Flask static server for local development (fixes CORS for WASM/PyScript) ---
read -p "[?] Do you want to run a local Flask server for index.html? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
cat > serve.py <<EOF
from flask import Flask, send_from_directory
app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)
if __name__ == '__main__':
    app.run(port=5000)
EOF
    echo "[*] Run your app with: python serve.py"
fi

echo "[*] PyScript integration patch complete!"