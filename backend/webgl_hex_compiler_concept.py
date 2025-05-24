# backend/webgl_hex_compiler_concept.py
# This script simulates a hex-to-WebGL compiler.
# It takes a hex string, conceptually processes it, and returns
# simulated GLSL shader code and vertex data as a JSON string.
# This JSON is then parsed by the JavaScript frontend to update the WebGL canvas.

import sys
import binascii
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WebGL_Hex_Compiler')

def compile_hex_to_webgl(hex_input):
  """
  Conceptually "compiles" a hexadecimal string into WebGL data.
  This function will generate simulated GLSL shaders and vertex data
  based on the input hex, returning it as a JSON string.
  """
  logger.info(f"Conceptual WebGL compilation started for hex: {hex_input[:50]}...")

  output_data = {
    "status": "success",
    "message": "Conceptual WebGL data generated.",
    "vertexShaderCode": "",
    "fragmentShaderCode": "",
    "vertexData": [],
    "backgroundColor": [0.1, 0.1, 0.1, 1.0], # Default dark
    "shapeType": "triangle" # Default shape
  }

  try:
    # 1. Decode hex to bytes
    # Ensure hex string has even length, pad if necessary
    if len(hex_input) % 2 != 0:
      hex_input = '0' + hex_input # Pad with leading zero

    decoded_bytes = binascii.unhexlify(hex_input)
    decoded_ascii = decoded_bytes.decode('utf-8', errors='ignore')

    logger.info(f"Decoded bytes length: {len(decoded_bytes)}. ASCII: '{decoded_ascii}'")

    # 2. Derive conceptual parameters from hex input
    # Use first few bytes to influence color, shape, etc.
    color_r = (decoded_bytes[0] / 255.0) if len(decoded_bytes) > 0 else 0.1
    color_g = (decoded_bytes[1] / 255.0) if len(decoded_bytes) > 1 else 0.5
    color_b = (decoded_bytes[2] / 255.0) if len(decoded_bytes) > 2 else 0.8

    output_data["backgroundColor"] = [color_r, color_g, color_b, 1.0]

    # Determine shape based on hex length or a byte value
    if len(decoded_bytes) % 3 == 0:
      output_data["shapeType"] = "triangle"
    elif len(decoded_bytes) % 4 == 0:
      output_data["shapeType"] = "square"
    elif len(decoded_bytes) % 5 == 0:
      output_data["shapeType"] = "line"
    else:
      output_data["shapeType"] = "point"

    # Generate simple vertex data based on hex content length
    # For simplicity, we just generate a fixed set of vertices.
    # In a real compiler, this would parse geometric data from hex.
    if output_data["shapeType"] == "triangle":
      output_data["vertexData"] = [
        -0.5, -0.5,  # Bottom left
        0.5, -0.5,  # Bottom right
        0.0,  0.5   # Top middle
      ]
    elif output_data["shapeType"] == "square":
      output_data["vertexData"] = [
        -0.5,  0.5,  # Top-left
        -0.5, -0.5,  # Bottom-left
        0.5, -0.5,  # Bottom-right
        0.5,  0.5   # Top-right
      ]
    elif output_data["shapeType"] == "line":
      output_data["vertexData"] = [-0.8, 0.0, 0.8, 0.0]
    else: # point
      output_data["vertexData"] = [0.0, 0.0]

    # 3. Generate simulated GLSL shaders
    # These are basic, functional shaders that the frontend can use.
    output_data["vertexShaderCode"] = """
precision mediump float;
attribute vec2 a_position;

void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""
    output_data["fragmentShaderCode"] = f"""
precision mediump float;
uniform vec4 u_color;

void main() {{
    gl_FragColor = u_color;
}}
"""
    output_data["message"] = (
      f"Conceptually compiled hex (first 50 chars: '{hex_input[:50]}...') "
      f"into a {output_data['shapeType']} with color {output_data['backgroundColor']} "
      f"on the WebGL canvas."
    )

  except binascii.Error:
    output_data["status"] = "error"
    output_data["message"] = "Invalid hexadecimal string format. Please provide valid hex."
    logger.error(f"Invalid hex input: {hex_input}")
  except Exception as e:
    output_data["status"] = "error"
    output_data["message"] = f"An unexpected error occurred: {str(e)}"
    logger.error(f"Error during hex_to_webgl conceptual compilation: {e}", exc_info=True)

  # Return the structured data as a JSON string
  return json.dumps(output_data)

if __name__ == '__main__':
  # This script is designed to be called by compiler_runner.py
  # It receives the hex string as the first command-line argument.
  if len(sys.argv) > 1:
    hex_string_from_cli = sys.argv[1]
    print(compile_hex_to_webgl(hex_string_from_cli))
  else:
    # If run directly without arguments, provide usage info
    print("Usage: python webgl_hex_compiler_concept.py <hex_string>")
    print("This script is meant to be called by the OBPI backend's compiler_runner.py.")
    print("Example: python webgl_hex_compiler_concept.py 48656C6C6F") # "Hello" in hex
    # Provide a default conceptual output for direct testing
    print(compile_hex_to_webgl("000102030405060708090a0b0c0d0e0f"))
