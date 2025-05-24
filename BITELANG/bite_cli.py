import argparse
import subprocess
import os
from bite_ide import BITEIDE

class BITECLI:
    def __init__(self):
        self.ide = BITEIDE()

    def run(self, args):
        if args.command == "run":
            self.run_bite_code(args.file)
        elif args.command == "edit":
            self.ide.open_file(args.file)
        elif args.command == "new":
            self.ide.create_new_file(args.file, args.template)
        elif args.command == "compile":
            self.ide.compile_file(args.file, args.target)
        else:
            print("Unknown command. Use --help.")

    def run_bite_code(self, filename):
        ext = os.path.splitext(filename)[1]
        if ext == ".b":
            # Future: parse/interpret BITE code
            print(f"[BITECLI] Running BITE code: {filename} (simulated)")
            with open(filename) as f:
                code = f.read()
            exec(code, {})  # Very basic; replace with real BITE VM
        elif ext == ".c":
            # Compile and run C using system compiler
            print(f"[BITECLI] Compiling and running C code: {filename}")
            executable = filename.replace(".c", "")
            subprocess.run(["gcc", filename, "-o", executable])
            subprocess.run([f"./{executable}"])
        elif ext == ".py":
            print(f"[BITECLI] Running Python code: {filename}")
            subprocess.run(["python3", filename])
        else:
            print(f"[BITECLI] Unsupported file type: {ext}")

def main():
    parser = argparse.ArgumentParser(description="BITE CLI: Run and manage BITE code")
    subparsers = parser.add_subparsers(dest="command")

    parser_run = subparsers.add_parser("run", help="Run a BITE code file")
    parser_run.add_argument("file", help="File to run (.b, .c, .py)")

    parser_edit = subparsers.add_parser("edit", help="Edit a BITE code file")
    parser_edit.add_argument("file", help="File to edit")

    parser_new = subparsers.add_parser("new", help="Create a new BITE code file")
    parser_new.add_argument("file", help="Filename")
    parser_new.add_argument("--template", help="Template type (bite/c/python)", default="bite")

    parser_compile = subparsers.add_parser("compile", help="Compile a BITE code file")
    parser_compile.add_argument("file", help="File to compile")
    parser_compile.add_argument("--target", help="Target (wasm/native)", default="native")

    args = parser.parse_args()
    cli = BITECLI()
    cli.run(args)

if __name__ == "__main__":
    main()