import os
import json
import firebase_admin
import bleach
import requests
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, jsonify
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
# This looks for a .env file in the same directory as this app.py file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f".env file loaded successfully from: {dotenv_path}")
else:
    print(f"CRITICAL: .env file NOT found at the expected path: {dotenv_path}")

# --- Flask App and Auth Initialization ---
app = Flask(__name__)
auth = HTTPBasicAuth()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"
GOOGLE_CLOUD_PROJECT = "madewhere-e009e" 

users = {
    ADMIN_USERNAME: ADMIN_PASSWORD
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

# --- Firebase Initialization ---
db = None
if not firebase_admin._apps:
    try:
        cred_path = os.path.join(app.root_path, 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase App initialized successfully.")
    except Exception as e:
        print(f"CRITICAL: Firebase initialization failed. Check your serviceAccountKey.json.")
        print(f"Error: {e}")
        pass

if firebase_admin._apps:
    db = firestore.client()

# --- Page Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin')
@auth.login_required
def admin():
    return render_template('admin.html')

# --- API Routes ---
@app.route('/api/brands')
def get_brands():
    if db is None: return jsonify({"error": "Database not connected."}), 500
    try:
        docs = db.collection('brands').stream()
        brands_list = [doc.to_dict() for doc in docs]
        return jsonify(brands_list)
    except Exception as e:
        print(f"Error fetching from Firestore: {e}")
        return jsonify({"error": "Could not load brand data."}), 500

@app.route('/api/suggestions')
@auth.login_required
def get_suggestions():
    if db is None: return jsonify({"error": "Database not connected."}), 500
    try:
        sug_ref = db.collection('suggestions').where('status', '==', 'new')
        docs = sug_ref.stream()
        suggestions = []
        for doc in docs:
            suggestion = doc.to_dict()
            suggestion['id'] = doc.id
            suggestions.append(suggestion)
        return jsonify(suggestions)
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return jsonify({"error": "Could not get suggestions."}), 500

@app.route('/api/research/<suggestion_id>', methods=['POST'])
@auth.login_required
def research_suggestion(suggestion_id):
    if db is None: return jsonify({"error": "Database not connected."}), 500
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("CRITICAL: os.getenv('GEMINI_API_KEY') returned None. The key was not loaded from the .env file.")
        return jsonify({"error": "GEMINI_API_KEY not found in environment. Check terminal logs and .env file."}), 500
    else:
        print(f"API Key loaded successfully, starting with: {api_key[:4]}...")

    try:
        suggestion_ref = db.collection('suggestions').document(suggestion_id)
        suggestion = suggestion_ref.get().to_dict()
        if not suggestion or 'brand_website' not in suggestion:
            return jsonify({"error": "Invalid suggestion data"}), 404
        
        try:
            site_response = requests.get(suggestion['brand_website'], timeout=15)
            site_content = bleach.clean(site_response.text, strip=True)[:15000]
        except requests.RequestException as e:
            return jsonify({"error": f"Could not browse website: {e}"}), 500

        prompt = f"""
        Analyze the following website content for the company named "{suggestion['brand_name']}". Based *only* on the text provided, extract the following information.

        Website Content:
        ---
        {site_content}
        ---

        Please fill in the JSON object below with your findings.
        - "summary": A one-sentence summary of the company.
        - "verdict": A one-sentence verdict on their manufacturing claims (e.g., "All products are made in their Ohio factory.").
        - "location": The primary City, ST of their manufacturing or HQ.
        - "state": The two-letter state abbreviation.
        - "region": One of the following: new_england, northeast, southeast, appalachia, rust_belt, midwest, southwest, mountain_west, pacific, west_coast.
        - "categories": A list of relevant categories from: furniture, outdoor, kitchen, apparel, tools, food, beverages, bikes, pets, home_goods, personal_care.
        - "tags": A list of relevant tags from: made_in_usa, assembled_in_usa, us_owned, foreign_owned, verified, reported. Assume 'reported' unless explicitly stated otherwise.
        """
        
        api_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json", "response_schema": {"type": "OBJECT", "properties": { "summary": {"type": "STRING"}, "verdict": {"type": "STRING"}, "location": {"type": "STRING"}, "state": {"type": "STRING"}, "region": {"type": "STRING"}, "categories": {"type": "ARRAY", "items": {"type": "STRING"}}, "tags": {"type": "ARRAY", "items": {"type": "STRING"}}}}}}
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_endpoint, json=payload, headers=headers)
        
        if response.status_code != 200:
            error_details = response.text
            print(f"--- GEMINI API ERROR ---\nStatus Code: {response.status_code}\nResponse: {error_details}\n------------------------")
            return jsonify({"error": f"Google API Error: {response.status_code} - {error_details}"}), 500

        response_json = response.json()
        researched_data = json.loads(response_json['candidates'][0]['content']['parts'][0]['text'])
        return jsonify(researched_data)

    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500

# ... (approve and reject routes are unchanged) ...
@app.route('/api/approve/<suggestion_id>', methods=['POST'])
@auth.login_required
def approve_suggestion(suggestion_id):
    if db is None: return jsonify({"error": "Database not connected."}), 500
    try:
        data = request.get_json()
        sanitized_data = {key: bleach.clean(str(value)) for key, value in data.items()}
        brand_name = sanitized_data.get('name')

        brands_ref = db.collection('brands')
        query = brands_ref.where('name', '==', brand_name).limit(1)
        existing = list(query.stream())
        if existing:
            return jsonify({"error": f"A brand named '{brand_name}' already exists."}), 409

        suggestion_ref = db.collection('suggestions').document(suggestion_id)
        suggestion_ref.update({"status": "approved"})

        max_id_query = brands_ref.order_by("id", direction=firestore.Query.DESCENDING).limit(1)
        docs = list(max_id_query.stream())
        last_id = docs[0].to_dict().get('id', 0) if docs else 0
        new_id = last_id + 1

        new_brand_data = {
            "id": new_id, "name": brand_name, "website": sanitized_data.get('website'), "summary": sanitized_data.get('summary'), "verdict": sanitized_data.get('verdict'), "location": sanitized_data.get('location'), "state": sanitized_data.get('state', '').upper(), "region": sanitized_data.get('region'), "categories": [cat.strip() for cat in sanitized_data.get('categories', '').split(',') if cat.strip()], "tags": [tag.strip() for tag in sanitized_data.get('tags', '').split(',') if tag.strip()], "coordinates": None, "logo": f"https://placehold.co/100x40/e2e8f0/4a5568?text={brand_name.replace(' ', '+')}"
        }
        
        brands_ref.document(str(new_id)).set(new_brand_data)
        return jsonify({"status": "success", "message": f"Brand {new_id} approved."})

    except Exception as e:
        print(f"Error approving suggestion: {e}")
        return jsonify({"error": "Approval failed."}), 500

@app.route('/api/reject/<suggestion_id>', methods=['POST'])
@auth.login_required
def reject_suggestion(suggestion_id):
    if db is None: return jsonify({"error": "Database not connected."}), 500
    try:
        suggestion_ref = db.collection('suggestions').document(suggestion_id)
        suggestion_ref.update({"status": "rejected"})
        return jsonify({"status": "success", "message": "Suggestion rejected."})
    except Exception as e:
        print(f"Error rejecting suggestion: {e}")
        return jsonify({"error": "Rejection failed."}), 500

@app.route('/suggest', methods=['POST'])
def suggest():
    if db is None: return jsonify({"error": "Database not connected."}), 500
    try:
        data = request.get_json()
        suggestion_data = {
            'brand_name': bleach.clean(data.get('brand_name')),
            'brand_website': bleach.clean(data.get('brand_website')),
            'timestamp': firestore.SERVER_TIMESTAMP,
            'status': 'new'
        }
        db.collection('suggestions').add(suggestion_data)
        return jsonify({'status': 'success', 'message': 'Thank you for your suggestion!'})
    except Exception as e:
        print(f"Error saving suggestion: {e}")
        return jsonify({"error": "Could not save suggestion."}), 500


if __name__ == '__main__':
    app.run(debug=True)
