# migration_add_fields.py
# A one-time script to add 'tags' and 'regions' fields to all brand documents.

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# --- SETUP ---
# 1. Authenticate with Firebase using your service account key.
#    Make sure 'serviceAccountKey.json' is in the same directory as this script.
try:
    cred = credentials.Certificate("serviceAccountKey_firebase.json")
    firebase_admin.initialize_app(cred)
    print("✅ Successfully authenticated with Firebase.")
except Exception as e:
    print(f"🔥 Authentication failed: {e}")
    print("👉 Please ensure 'serviceAccountKey.json' is in the correct path.")
    exit()

# 2. Get a reference to the Firestore database.
db = firestore.client()
print("✅ Database client initialized.")

# --- MIGRATION LOGIC ---
def migrate_brands():
    """
    Fetches all documents from the 'brands' collection and adds empty
    'tags' and 'regions' arrays to each if they don't exist.
    """
    # 3. Get a reference to the 'brands' collection.
    brands_ref = db.collection('brands')
    docs = brands_ref.stream() # Use .stream() for efficiency with large collections

    print("\n🚀 Starting migration...")
    update_count = 0
    
    # 4. Iterate through each document.
    for doc in docs:
        brand_data = doc.to_dict()
        brand_id = doc.id
        
        # 5. Check if the fields already exist to avoid unnecessary writes.
        if 'tags' not in brand_data or 'regions' not in brand_data:
            print(f"Updating brand: {brand_data.get('name', brand_id)}...")
            
            # 6. Perform the update. This adds the fields without deleting existing data.
            doc.reference.update({
                'tags': [],
                'regions': []
            })
            update_count += 1
        else:
            print(f"Skipping brand (fields exist): {brand_data.get('name', brand_id)}")

    print("\n🎉 Migration complete!")
    print(f"Total documents updated: {update_count}")

# --- EXECUTE SCRIPT ---
if __name__ == "__main__":
    migrate_brands()
