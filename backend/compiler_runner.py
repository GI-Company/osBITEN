# backend/compiler_runner.py
import subprocess
import os
import sys
import platform
import logging
import tempfile
import json # Import json for structured output

logger = logging.getLogger('Compiler_Runner')

class CompilerRunner:
  def __init__(self):
    self.compilers = {
      'c': {'cmd': 'gcc', 'flags': ['-o', 'output.exe'], 'ext': '.c', 'run_cmd': './output.exe'},
      'cpp': {'cmd': 'g++', 'flags': ['-o', 'output.exe'], 'ext': '.cpp', 'run_cmd': './output.exe'},
      'csharp': {'cmd': 'dotnet', 'flags': ['run'], 'ext': '.cs', 'is_script': True},
      'go': {'cmd': 'go', 'flags': ['run'], 'ext': '.go', 'is_script': True},
      'rust': {'cmd': 'rustc', 'flags': ['-o', 'output.exe'], 'ext': '.rs', 'run_cmd': './output.exe'},
      'haskell': {'cmd': 'ghc', 'flags': ['-o', 'output.exe'], 'ext': '.hs', 'run_cmd': './output.exe'},
      'cobol': {'cmd': 'cobc', 'flags': ['-x', '-o', 'output.exe'], 'ext': '.cbl', 'run_cmd': './output.exe'},
      'fortran': {'cmd': 'gfortran', 'flags': ['-o', 'output.exe'], 'ext': '.f90', 'run_cmd': './output.exe'},
      'lua': {'cmd': 'lua', 'flags': [], 'ext': '.lua', 'is_script': True},
      'emcc': {'cmd': 'emcc', 'flags': ['-o', 'output.html'], 'ext_map': {'c':'.c', 'cpp':'.cpp'}, 'is_emcc': True},
      # Special entry for hex_to_webgl, it points to our conceptual script
      'hex_to_webgl': {'cmd': sys.executable, 'script': os.path.join(os.path.dirname(__file__), 'webgl_hex_compiler_concept.py'), 'is_custom_script': True}
    }
    self._check_compiler_paths()

  def _check_compiler_paths(self):
    """Checks if required compilers are in PATH and logs their status."""
    logger.info("Checking external compiler availability...")
    for lang, info in self.compilers.items():
      if 'cmd' in info and not info.get('is_script') and not info.get('is_emcc') and not info.get('is_custom_script'):
        try:
          subprocess.run([info['cmd'], '--version'], capture_output=True, check=True, text=True, timeout=5)
          logger.info(f"Compiler '{info['cmd']}' for {lang.upper()} found.")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
          logger.warning(f"Compiler '{info['cmd']}' for {lang.upper()} not found or not callable. "
                         f"Please ensure it's installed and in your system's PATH to use this feature.")
      elif info.get('is_emcc'):
        try:
          subprocess.run([info['cmd'], '--version'], capture_output=True, check=True, text=True, timeout=5)
          logger.info(f"Compiler '{info['cmd']}' (Emscripten) found.")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
          logger.warning(f"Emscripten compiler '{info['cmd']}' not found. Emcc compilation will be conceptual.")


  def compile_and_run_code(self, lang, code_content, emcc_lang=None):
    logger.info(f"Attempting to compile and run {lang.upper()} code.")
    compiler_info = self.compilers.get(lang)

    if not compiler_info:
      return {"status": "error", "output": f"Unsupported language: {lang}"}

    # Create a temporary directory for compilation/execution
    with tempfile.TemporaryDirectory() as tmpdir:
      try:
        if compiler_info.get('is_custom_script'):
          # Special handling for custom Python scripts like hex_to_webgl
          command = [compiler_info['cmd'], compiler_info['script'], code_content]
          logger.info(f"Executing custom script: {' '.join(command)}")
          # For hex_to_webgl, we expect JSON output from the script
          result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=os.getcwd())

          if result.returncode != 0:
            logger.error(f"Custom script failed: {result.stderr}")
            return {"status": "error", "output": f"Script Error:\n{result.stdout}\n{result.stderr}"}
          else:
            try:
              # Attempt to parse the output as JSON
              json_output = json.loads(result.stdout.strip())
              logger.info(f"Custom script returned JSON: {json_output}")
              return {"status": "success", "output": json_output}
            except json.JSONDecodeError:
              logger.error(f"Custom script output is not valid JSON: {result.stdout}")
              return {"status": "error", "output": f"Script output is not valid JSON:\n{result.stdout}\n{result.stderr}"}

        # Determine file extension
        ext = compiler_info.get('ext')
        if lang == 'emcc':
          if emcc_lang not in compiler_info['ext_map']:
            return {"status": "error", "output": f"EMCC: Unsupported source language '{emcc_lang}' for Emscripten."}
          ext = compiler_info['ext_map'][emcc_lang]

        source_file_name = f"temp_source{ext}"
        source_file_path = os.path.join(tmpdir, source_file_name)

        # Write code content to a temporary file
        with open(source_file_path, 'w', encoding='utf-8') as f:
          f.write(code_content)
        logger.info(f"Source code written to temporary file: {source_file_path}")

        compile_cmd = [compiler_info['cmd']]
        if not compiler_info.get('is_script') and lang != 'emcc': # Add source file and output flags for compiled langs
          compile_cmd.append(source_file_path)
          compile_cmd.extend(compiler_info['flags'])
          compile_cmd.append(os.path.join(tmpdir, compiler_info['flags'][1])) # output.exe or similar
        elif lang == 'emcc':
          # Emscripten specific flags for C/C++ to WASM/JS
          compile_cmd.append(source_file_path)
          # For a truly conceptual output, just return a message.
          # If you want real output from emcc, add:
          # compile_cmd.extend(['-s', 'WASM=1', '-o', os.path.join(tmpdir, 'output.js')]) # Emscripten often outputs .js
          # For this conceptual implementation, we just simulate success.
          logger.warning("EMCC compilation is conceptual; actual WASM/JS output is not consumed here.")
          # Return a simulated success for EMCC
          return {"status": "success", "output": f"Conceptual EMCC compilation of '{source_file_name}' to WebAssembly/JS (output.html) simulated successfully. Actual compilation requires Emscripten SDK."}
        elif compiler_info.get('is_script'): # For interpreted languages like Go, Lua, C# dotnet run
          compile_cmd.extend(compiler_info['flags'])
          compile_cmd.append(source_file_path)

        # Execute the compilation command
        logger.info(f"Compilation command: {' '.join(compile_cmd)} (cwd: {tmpdir})")
        # Use check=False to capture stderr even if command fails
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=tmpdir, check=False)

        if compile_result.returncode != 0:
          logger.error(f"Compilation failed for {lang}: {compile_result.stderr}")
          return {"status": "error", "output": f"Compilation Error:\n{compile_result.stdout}\n{compile_result.stderr}"}

        if compiler_info.get('is_script'):
          # For script languages, the 'compile_result' already contains the run output
          logger.info(f"Script run output for {lang}: {compile_result.stdout}")
          return {"status": "success", "output": compile_result.stdout}
        else:
          # If compiled, now run the executable
          run_cmd = compiler_info['run_cmd'].split()
          run_executable_path = os.path.join(tmpdir, os.path.basename(run_cmd[0]))

          # Special handling for Windows executables (add .exe if missing)
          if platform.system() == "Windows" and not run_executable_path.lower().endswith(".exe"):
            run_executable_path += ".exe"

          run_cmd[0] = run_executable_path # Ensure path to executable is correct

          logger.info(f"Execution command: {' '.join(run_cmd)} (cwd: {tmpdir})")
          run_result = subprocess.run(run_cmd, capture_output=True, text=True, cwd=tmpdir, check=False)

          output = compile_result.stdout + "\n" + compile_result.stderr + "\n" + run_result.stdout + "\n" + run_result.stderr
          if run_result.returncode != 0:
            logger.error(f"Execution failed for {lang}: {run_result.stderr}")
            return {"status": "error", "output": f"Execution Error:\n{output}"}
          else:
            logger.info(f"Execution successful for {lang}: {run_result.stdout}")
            return {"status": "success", "output": output}

      except FileNotFoundError as fnfe:
        logger.error(f"Compiler command '{compiler_info['cmd']}' not found for {lang.upper()}. Please install it and ensure it's in your system's PATH. Error: {fnfe}")
        return {"status": "error", "output": f"Compiler '{compiler_info['cmd']}' not found. Please install the {lang.upper()} compiler."}
      except Exception as e:
        logger.error(f"An unexpected error occurred during {lang} compilation/execution: {e}", exc_info=True)
        return {"status": "error", "output": f"An unexpected error occurred: {str(e)}"}
