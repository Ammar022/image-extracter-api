import os
import base64
from flask import Flask, jsonify, Response, request # <-- Import 'request'
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
# Get credentials from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
# These are for the repo you want to READ FROM
REPO_OWNER = 'israr'
REPO_NAME = 'image-extracter-api'

# --- Securely map query parameters to file paths ---
# This prevents users from accessing unintended files.
# Add a new entry here for every pipeline file you want to expose.
PIPELINE_FILE_MAP = {
    "sex_offender": "gichi michi"
    # Add other mappings here, for example:
    # "another_pipeline": "path/to/its/file.py"
}

@app.route('/api/get-remote-code')
def get_remote_code():
    """Fetches a specific pipeline file from a private GitHub repo based on a query parameter."""

    # 1. Get the pipeline identifier from the query parameters
    pipeline_name = request.args.get('pipeline')

    # 2. Validate the input
    if not pipeline_name:
        return jsonify({"message": "Missing 'pipeline' query parameter."}), 400 # Bad Request

    # 3. Look up the file path in our secure map
    file_path = PIPELINE_FILE_MAP.get(pipeline_name)

    if not file_path:
        return jsonify({"message": f"Pipeline '{pipeline_name}' not found or is not configured."}), 404 # Not Found
    
    # --- The rest of the logic is the same ---
    api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}'
    
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        
        data = response.json()
        
        if 'content' in data:
            file_content_b64 = data['content']
            decoded_content = base64.b64decode(file_content_b64).decode('utf-8')
            return Response(decoded_content, mimetype='text/plain')
        else:
            return jsonify({"message": "Content not found in API response."}), 404

    except requests.exceptions.RequestException as e:
        # This will catch network errors or 4xx/5xx responses from GitHub
        error_message = f"Error fetching file from GitHub: {e}"
        if e.response is not None:
            error_message += f" | Response: {e.response.text}"
        print(error_message)
        return jsonify({"message": "Failed to fetch file from the remote repository."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
