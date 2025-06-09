from flask import Flask, request, jsonify
from generate_response import generate_response
import os
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get the expected token from environment variables
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header is present
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expecting "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Bearer token malformed"}), 401
        
        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401
        
        if token != API_AUTH_TOKEN:
            return jsonify({"error": "Invalid authorization token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/api/answer', methods=['POST'])
@token_required  # Add this decorator to protect the endpoint
def get_answer():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
            
        query = data['query']
        top_k = data.get('top_k', 3)
        
        # Generate response
        response = generate_response(query, top_k)
        
        return jsonify({
            "query": query,
            "response": response,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)