from flask import Flask, request, jsonify
from bitenlang import run_biten_code

app = Flask(__name__)

@app.route("/run_biten", methods=["POST"])
def run_biten():
    code = request.json.get("code", "")
    output_lines = []
    def output_func(line):
        output_lines.append(line)
    try:
        run_biten_code(code, output_func=output_func)
        return jsonify({"success": True, "output": "\n".join(output_lines)})
    except Exception as e:
        return jsonify({"success": False, "output": f"Error: {e}"}), 400

if __name__ == "__main__":
    app.run(port=5005)