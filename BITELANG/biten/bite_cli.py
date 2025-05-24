import argparse
import os
import subprocess
from bite_compiler import build_bite, run_bite
from bite_ide import launch_ide

def create_project(name, lang):
    templates = {
        "bite": "templates/template.b",
        "c": "templates/template.c",
        "python": "templates/template.py"
    }
    if lang not in templates:
        print(f"Unsupported language: {lang}")
        return
    with open(templates[lang]) as src, open(f"{name}.{lang[0]}", "w") as dst:
        dst.write(src.read())
    print(f"Created {name}.{lang[0]}")

def main():
    parser = argparse.ArgumentParser(description="BITE CLI")
    parser.add_argument("command", choices=["new", "build", "run", "edit", "ide"])
    parser.add_argument("file", nargs="?", help="File or project name")
    parser.add_argument("--lang", default="bite", help="Language: bite, c, python")
    args = parser.parse_args()

    if args.command == "new":
        if not args.file:
            print("Specify a project name.")
        else:
            create_project(args.file, args.lang)
    elif args.command == "build":
        if not args.file:
            print("Specify a source file.")
        else:
            build_bite(args.file)
    elif args.command == "run":
        if not args.file:
            print("Specify a source file.")
        else:
            run_bite(args.file)
    elif args.command == "edit":
        if not args.file:
            print("Specify a file to edit.")
        else:
            launch_ide(args.file)
    elif args.command == "ide":
        launch_ide()
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()