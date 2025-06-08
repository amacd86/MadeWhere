import os
import json
from flask import Flask, render_template, request, jsonify

# Initialize the Flask app
app = Flask(__name__)

# --- Primary Page Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- API Routes ---

@app.route('/api/brands')
def get_brands():
    try:
        # Construct the full path to the JSON file
        json_file_path = os.path.join(app.root_path, 'brands.json')
        with open(json_file_path, 'r') as f:
            brands_data = json.load(f)
        return jsonify(brands_data)
    except Exception as e:
        # Log the error for debugging and return an error response
        print(f"Error reading brands.json: {e}")
        return jsonify({"error": "Could not load brand data."}), 500

@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.get_json()
    brand_name = data.get('brand_name')
    brand_website = data.get('brand_website')

    print("--- New Brand Suggestion Received ---")
    print(f"Brand Name: {brand_name}")
    print(f"Website: {brand_website}")
    print("------------------------------------")
    
    return jsonify({'status': 'success', 'message': 'Thank you for your suggestion!'})

if __name__ == '__main__':
    app.run(debug=True)