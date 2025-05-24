# backend/ai_core.py
import json
import binascii
import logging
from datetime import datetime

logger = logging.getLogger('AI_Core')

class AICore:
  def __init__(self):
    logger.info("AI Core initialized.")

  def process_query(self, query):
    logger.info(f"AI: Processing query: '{query}'")
    query_lower = query.lower().strip()

    # Rule-based responses for demonstration
    if "hello" in query_lower or "hi assistant" in query_lower:
      response = "Hello! How can I assist you today?"
    elif "time" in query_lower:
      response = f"The current time is {datetime.now().strftime('%H:%M:%S')}."
    elif "date" in query_lower:
      response = f"Today's date is {datetime.now().strftime('%Y-%m-%d')}."
    elif "how are you" in query_lower:
      response = "I am a large language model, I do not have feelings, but I am ready to help you!"
    elif "capabilities" in query_lower or "what can you do" in query_lower:
      response = "I can help with file system operations (conceptual), hex conversions, and answer general questions based on my training data. Try asking me to 'convert text to hex' or 'generate C hex for Hello World'."
    elif "convert c print hello to hex" in query_lower:
      # Example for generating conceptual C hex
      c_code = 'printf("Hello World\\n");'
      hex_output = self.text_to_hex(c_code)
      return {
        "response_text": "Here's a conceptual hex representation for 'printf(\"Hello World\\n\");' in C:",
        "generated_hex": f"// C conceptual hex for: {c_code}\n"
                         f"48656C6C6F20576F726C640A00 // ASCII for 'Hello World\\n\\0'\n"
                         f"8B010100             // Example: call printf function (simulated)\n"
                         f"// Note: This is highly conceptual and not a true compiler output.\n"
                         f"// Real C compilation is complex and depends on architecture, libraries, etc."
                         f"// For real C compilation, use the 'c_compile' CLI command with a .c file.",
        "language": "c"
      }
    elif "generate python hex" in query_lower:
      python_code = 'print("Python Hex Example")'
      hex_output = self.text_to_hex(python_code)
      return {
        "response_text": "Here's a conceptual hex representation for Python code:",
        "generated_hex": f"// Python conceptual hex for: {python_code}\n"
                         f"7072696E742822507974686F6E20486578204578616D706C652229 // ASCII for 'print(\"Python Hex Example\")'\n"
                         f"// Note: Python bytecode is not directly hex-encoded source code.",
        "language": "python"
      }
    elif "convert text to hex" in query_lower:
      response = "Please provide the text you want to convert to hex using the Hex Converter tab."
    elif "convert hex to text" in query_lower:
      response = "Please provide the hex string you want to convert to text using the Hex Converter tab."
    else:
      # Placeholder for actual LLM integration
      response = "I'm a conceptual AI assistant. For more complex queries, I'd connect to a powerful LLM. For now, I offer basic command support. Try 'what can you do?'"

    return {"response_text": response, "generated_hex": None, "language": None}

  def text_to_hex(self, text_input):
    logger.info(f"AI: Converting text to hex: '{text_input[:50]}...'")
    try:
      # Encode text to bytes, then to hex
      hex_output = binascii.hexlify(text_input.encode('utf-8')).decode('utf-8')
      return {"hex_output": hex_output, "error": None}
    except Exception as e:
      logger.error(f"Error converting text to hex: {e}")
      return {"hex_output": None, "error": str(e)}

  def hex_to_text(self, hex_input):
    logger.info(f"AI: Converting hex to text: '{hex_input[:50]}...'")
    try:
      # Ensure hex string has even length, pad if necessary
      if len(hex_input) % 2 != 0:
        hex_input = '0' + hex_input # Pad with leading zero

      # Decode hex to bytes, then to text
      text_output = binascii.unhexlify(hex_input).decode('utf-8')
      return {"text_output": text_output, "error": None}
    except binascii.Error as e:
      logger.error(f"Invalid hex string: {e}")
      return {"text_output": None, "error": f"Invalid hexadecimal string: {e}"}
    except Exception as e:
      logger.error(f"Error converting hex to text: {e}")
      return {"text_output": None, "error": str(e)}

# Global AI instance (or initialize in main.py)
# ai_core = AICore()
