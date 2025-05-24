import os
import subprocess
import sys
from bitenlang import run_biten_code

def build_bite(filename):
    ext = os.path.splitext(filename)[1]
    if ext == ".c":
        output = filename[:-2]
        result = subprocess.run(["gcc", filename, "-O2", "-o", output])
        if result.returncode == 0:
            print(f"Built {output}")
        else:
            print(f"Compilation failed.")
    elif ext == ".b":
        print("[BITEN] No build step needed for bitenlang.")
    elif ext == ".py":
        print("Python does not require building.")
    else:
        print("Unsupported file type.")

def run_bite(filename):
    ext = os.path.splitext(filename)[1]
    if ext == ".c":
        exe = filename[:-2]
        if not os.path.exists(exe):
            build_bite(filename)
        subprocess.run([f"./{exe}"])
    elif ext == ".b":
        with open(filename) as f:
            code = f.read()
        run_biten_code(code)
    elif ext == ".py":
        subprocess.run([sys.executable, filename])
    else:
        print("Unsupported file type.")