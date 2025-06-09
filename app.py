import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, jsonify

# --- Firebase Initialization ---
db = None
# This corrected block ensures the app is initialized only once.
if not firebase_admin._apps:
    try:
        # This path works for both local development and PythonAnywhere
        cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase App initialized successfully.")
    except Exception as e:
        print(f"CRITICAL: Firebase initialization failed. Check your serviceAccountKey.json.")
        print(f"Error: {e}")
        # The app will still run, but the API will return an error.
        pass
else:
    # If the app was already initialized (e.g., in a different process), get the client
    db = firestore.client()


# --- Flask App Initialization ---
app = Flask(__name__)


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

# --- API Routes ---

@app.route('/api/brands')
def get_brands():
    # Check if the database connection was successful
    if db is None:
        print("Firestore client is not available. Check initialization logs.")
        return jsonify({"error": "The database is not connected. Please check server logs."}), 500
    
    try:
        # Get all documents from the 'brands' collection in Firestore
        brands_ref = db.collection('brands')
        docs = brands_ref.stream()

        # Format the documents into a list of dictionaries
        brands_list = [doc.to_dict() for doc in docs]
        
        return jsonify(brands_list)
    except Exception as e:
        print(f"Error fetching from Firestore: {e}")
        return jsonify({"error": "Could not load brand data from database."}), 500

@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.get_json()
    brand_name = data.get('brand_name')
    brand_website = data.get('brand_website')

    print("--- New Brand Suggestion Received ---")
    print(f"Brand Name: {brand_name}")
    print(f"Website: {brand_website}")
    print("------------------------------------")
    
    # Here is where you would eventually add code to save the suggestion
    # to a 'suggestions' collection in Firestore.
    
    return jsonify({'status': 'success', 'message': 'Thank you for your suggestion!'})


if __name__ == '__main__':
    app.run(debug=True)
