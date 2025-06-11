# list_brands.py
# A simple script to list the name, id, and website of all brands
# for the AI to perform research.

import firebase_admin
from firebase_admin import credentials, firestore

# --- SETUP ---
# Standard authentication using your key file.
try:
    cred = credentials.Certificate("serviceAccountKey_firebase.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Successfully connected to Firestore. Fetching brands...\n")
except Exception as e:
    print(f"🔥 Authentication failed: {e}")
    exit()

# --- FETCH and PRINT ---
try:
    brands_ref = db.collection('brands')
    docs = brands_ref.stream()

    print("--- Brand List ---")
    for doc in docs:
        brand = doc.to_dict()
        # Use .get() to avoid errors if a field is missing
        brand_id = brand.get("id", "N/A")
        brand_name = brand.get("name", "Unknown Name")
        brand_website = brand.get("website", "No Website")
        print(f"ID: {brand_id}, Name: {brand_name}, Website: {brand_website}")
    print("--- End of List ---")

except Exception as e:
    print(f"An error occurred while fetching brands: {e}")
