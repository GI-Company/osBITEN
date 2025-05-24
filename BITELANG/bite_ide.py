import os

class BITEIDE:
    def __init__(self):
        pass

    def open_file(self, filename):
        if not os.path.exists(filename):
            print(f"[BITEIDE] File not found: {filename}")
            return
        with open(filename, "r") as f:
            content = f.read()
        print(f"--- Editing {filename} ---")
        print(content)
        print("--- End of file ---")
        # For real IDE: launch GUI/text editor here

    def create_new_file(self, filename, template="bite"):
        templates = {
            "bite": "// BITE code template\nfn main() {\n    println!(\"Hello, BITE world!\");\n}\n",
            "c": "#include <stdio.h>\nint main() {\n    printf(\"Hello, C world!\\n\");\n    return 0;\n}\n",
            "python": "print('Hello, Python world!')\n"
        }
        content = templates.get(template, templates["bite"])
        with open(filename, "w") as f:
            f.write(content)
        print(f"[BITEIDE] Created new file {filename} with template '{template}'.")

    def compile_file(self, filename, target="native"):
        # Stub to be replaced with real BITE compiler
        ext = os.path.splitext(filename)[1]
        if ext == ".b":
            print(f"[BITEIDE] Compiling BITE code: {filename} for {target} (simulated)")
            # TODO: Integrate BITE code -> WASM/native
        elif ext == ".c":
            print(f"[BITEIDE] Compiling C code: {filename} for {target}")
            output = filename.replace(".c", "")
            os.system(f"gcc {filename} -o {output}")
        elif ext == ".py":
            print("[BITEIDE] Python does not need compilation.")
        else:
            print(f"[BITEIDE] Unsupported file type: {ext}")