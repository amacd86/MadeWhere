# cleanup_delete_field.py
# A final script to remove the old, singular `region` field from all documents.

import firebase_admin
from firebase_admin import credentials, firestore

# --- SETUP ---
# Standard authentication using your key file.
try:
    cred = credentials.Certificate("serviceAccountKey_firebase.json")
    # Initialize the app if not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Successfully authenticated and connected to Firestore.")
except Exception as e:
    print(f"🔥 Authentication failed: {e}")
    exit()

# ==============================================================================
# CLEANUP LOGIC
# ==============================================================================

def delete_redundant_field():
    """
    Loops through all brands and deletes the 'region' field from each.
    """
    brands_ref = db.collection('brands')
    docs = brands_ref.stream()

    print("\n🚀 Starting cleanup: Looking for 'region' fields to delete...")
    delete_count = 0

    for doc in docs:
        brand_data = doc.to_dict()
        brand_id = doc.id

        # Check if the old 'region' field actually exists before trying to delete it
        if 'region' in brand_data:
            print(f"Deleting 'region' field from: {brand_data.get('name', brand_id)}...")
            
            # The special command to delete a field
            doc.reference.update({
                'region': firestore.DELETE_FIELD
            })
            delete_count += 1

    print("\n🎉 Cleanup complete!")
    print(f"Total documents affected: {delete_count}")


if __name__ == "__main__":
    delete_redundant_field()
