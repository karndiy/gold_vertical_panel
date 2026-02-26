from flask import Flask, render_template, request, jsonify
import os
import sys
import subprocess

app = Flask(__name__)

# Assume SCRIPT_DIR is the root of your project
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_video', methods=['POST'])
def generate_video():
    data = request.get_json()
    background_theme = data.get('background_theme', 'random')
    custom_message = data.get('custom_message', '')
    logo_url = data.get('logo_url', '')

    print(f"[WEB] Received video generation request:")
    print(f"[WEB]   Background Theme: {background_theme}")
    print(f"[WEB]   Custom Message: {custom_message if custom_message else 'N/A'}")
    print(f"[WEB]   Logo URL: {logo_url if logo_url else 'N/A'}")

    # This is a placeholder for future functionality
    # Here, we would trigger the main_workflow.py and pass parameters
    # For now, let's just confirm receipt and simulate running the workflow
    
    # In a real-world scenario, you'd use a task queue like Celery
    # to run long-running tasks like video generation in the background.
    try:
        # For simplicity, we'll just run the script and capture output
        # In the next step, we will pass these parameters to main_workflow.py or app.py
        # For now, just run main_workflow.py as before to confirm the web part works
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, 'main_workflow.py')],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
            timeout=600 # 10 minutes timeout for the whole workflow
        )
        
        if result.returncode == 0:
            return jsonify({"status": "success", "message": "Video generation workflow initiated successfully.", "output": result.stdout}), 200
        else:
            return jsonify({"status": "error", "message": "Video generation workflow failed.", "error_output": result.stderr, "output": result.stdout}), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Video generation workflow timed out."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    # For development, run with debug=True
    # In production, use a production-ready WSGI server like Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
