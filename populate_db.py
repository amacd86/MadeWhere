import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- IMPORTANT ---
# 1. Make sure your serviceAccountKey.json is in the same directory as this script.
# 2. Make sure your brands.json file is also in the same directory.
# 3. Run `pip install firebase-admin` in your terminal before running this script.
# This is a utility script. You'll run it from your terminal whenever you want to sync your brands.json file with your live Firestore database.

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase App initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase App: {e}")
    # If the app is already initialized, just get the instance
    if 'already exists' in str(e):
        app = firebase_admin.get_app()
        db = firestore.client(app=app)
        print("Firebase App was already initialized. Using existing instance.")
    else:
        exit()


# Path to your brands data
brands_json_path = 'brands.json'

# Get a reference to the 'brands' collection in Firestore
brands_collection = db.collection('brands')

print(f"Reading data from {brands_json_path}...")

# Open and read the JSON file
with open(brands_json_path, 'r') as f:
    brands_data = json.load(f)

print(f"Found {len(brands_data)} brands to upload.")

# Loop through each brand and upload it to Firestore
# We use the brand's 'id' as the document ID in Firestore for easy reference
for brand in brands_data:
    # Ensure the brand has an ID
    if 'id' in brand:
        doc_id = str(brand['id'])
        brands_collection.document(doc_id).set(brand)
        print(f"  - Uploaded: {brand['name']} (ID: {doc_id})")
    else:
        print(f"  - Skipped brand due to missing ID: {brand.get('name', 'Unknown')}")

print("\n-------------------------------------")
print("All brands have been uploaded to Firestore successfully!")
print("-------------------------------------")
