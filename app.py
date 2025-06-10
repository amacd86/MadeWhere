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
    # Check if the database connection was successful
    if db is None:
        print("Firestore client is not available. Cannot save suggestion.")
        return jsonify({"error": "The database is not connected. Please try again later."}), 500

    try:
        data = request.get_json()
        brand_name = data.get('brand_name')
        brand_website = data.get('brand_website')

        if not brand_name or not brand_website:
            return jsonify({'status': 'error', 'message': 'Missing brand name or website.'}), 400

        # Create a new document in a 'suggestions' collection
        suggestion_data = {
            'brand_name': brand_name,
            'brand_website': brand_website,
            'timestamp': firestore.SERVER_TIMESTAMP, # Use server time for consistency
            'status': 'new' # Default status for a new suggestion
        }
        
        # Add a new doc with a generated ID
        db.collection('suggestions').add(suggestion_data)

        print("--- New Brand Suggestion Saved to Firestore ---")
        print(f"Brand Name: {brand_name}")
        print(f"Website: {brand_website}")
        print("------------------------------------")
    
        return jsonify({'status': 'success', 'message': 'Thank you for your suggestion!'})

    except Exception as e:
        print(f"Error saving suggestion to Firestore: {e}")
        return jsonify({"error": "Could not save suggestion."}), 500

if __name__ == '__main__':
    app.run(debug=True)
