import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, jsonify

# --- Flask App Initialization ---
# We initialize the Flask app first so we can use its context to find our files.
app = Flask(__name__)


# --- Firebase Initialization ---
db = None
# This corrected block ensures the app is initialized only once.
if not firebase_admin._apps:
    try:
        # Build the path to the key file relative to the app's root path
        # This is a more robust way to find the file on any server.
        cred_path = os.path.join(app.root_path, 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase App initialized successfully.")
    except Exception as e:
        print(f"CRITICAL: Firebase initialization failed. Check your serviceAccountKey.json.")
        print(f"Error: {e}")
        # In a real app, you might want to handle this more gracefully
        # by logging the error and showing a user-friendly error page.
        pass

# Get a client instance for the Firestore database, only if initialization was successful
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
