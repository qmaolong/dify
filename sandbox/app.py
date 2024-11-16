from flask import Flask, request, jsonify
import subprocess
import os
import tempfile
from pydantic import BaseModel, ValidationError

app = Flask(__name__)

class CodeExecutionRequest(BaseModel):
    language: str
    code: str
    preload: str
    enable_network: bool

class CodeExecutionResponse(BaseModel):
    stdout: str
    stderr: str
    error: str
    
@app.route('/')
def home():
    return "hello world"

@app.route('/v1/sandbox/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        # Validate and parse request data
        execution_request = CodeExecutionRequest(**data)
        
        # Currently only support Python
        if not execution_request.language.lower().startswith("python"):
            return jsonify({
                "code": 1,
                "message": "Unsupported language"
            }), 400
        
        # Create a temporary directory to execute the code
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, 'script.py')
            with open(script_path, 'w') as script_file:
                script_file.write(execution_request.preload + '\n' + execution_request.code)
            
            # Execute the script
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=10  # Set a timeout for the execution
            )
            
            response_data = CodeExecutionResponse(
                stdout=result.stdout,
                stderr=result.stderr,
                error="" if result.returncode == 0 else result.stderr
            )
            
            return jsonify({
                "code": 0,
                "message": "ok",
                "data": response_data.dict()
            })
    
    except ValidationError as e:
        return jsonify({
            "code": 1,
            "message": "Invalid request data",
            "details": e.errors()
        }), 400
    except subprocess.TimeoutExpired:
        return jsonify({
            "code": 1,
            "message": "Code execution timeout"
        }), 500
    except Exception as e:
        return jsonify({
            "code": 1,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8194)
