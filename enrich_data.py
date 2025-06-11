# enrich_data.py
# A script to intelligently enrich Firestore documents with regions and tags
# based on predefined mapping rules.

import firebase_admin
from firebase_admin import credentials, firestore

# --- SETUP ---
try:
    # Use the key file you've already configured
    cred = credentials.Certificate("serviceAccountKey_firebase.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Successfully authenticated and connected to Firestore.")
except Exception as e:
    print(f"🔥 Authentication failed: {e}")
    exit()

# ==============================================================================
# STEP 1: YOUR KNOWLEDGE - EDIT THESE MAPPINGS
# ==============================================================================

# Teach the script which REGIONS belong to each STATE
# Add all your states and their corresponding regions here.
state_to_regions_map = {
    "MI": ["rust_belt", "midwest", "great_lakes"],
    "OH": ["rust_belt", "midwest", "appalachia"],
    "PA": ["rust_belt", "mid_atlantic", "northeast", "appalachia"],
    "NY": ["rust_belt", "mid_atlantic", "northeast"],
    "MN": ["midwest", "great_lakes"],
    "ME": ["new_england", "northeast", "east_coast"],
    # ... add more states as you add more brands
}

# Teach the script which TAGS to apply based on KEYWORDS
# The script will search for keywords in the brand's 'summary' and 'categories'
keyword_to_tag_map = {
    "furniture": "home_goods",
    "adaptable": "innovative_design",
    "apparel": "apparel",
    "clothing": "apparel",
    "denim": "apparel",
    "leather": "leather_goods",
    "bags": "accessories",
    "watch": "accessories",
    "watches": "accessories",
    "bicycle": "recreation",
    "bike": "recreation",
    "tool": "tools",
    # ... add more keywords and tags to make the script smarter
}


# ==============================================================================
# STEP 2: THE AUTOMATION LOGIC (No editing needed below this line)
# ==============================================================================

def enrich_data():
    """
    Loops through all brands, using the maps above to enrich their data.
    """
    brands_ref = db.collection('brands')
    docs = brands_ref.stream()
    
    print("\n🚀 Starting data enrichment...")
    update_count = 0

    for doc in docs:
        brand_data = doc.to_dict()
        brand_id = doc.id
        
        # Use sets to automatically handle duplicates
        regions_to_add = set()
        tags_to_add = set()

        # --- REGION LOGIC ---
        # 1. Add regions from the old `region` field if it exists
        if brand_data.get("region"):
            regions_to_add.add(brand_data["region"])
        
        # 2. Add regions based on the state mapping
        brand_state = brand_data.get("state")
        if brand_state and brand_state in state_to_regions_map:
            regions_to_add.update(state_to_regions_map[brand_state])

        # --- TAG LOGIC ---
        # Combine text sources to search for keywords
        search_text = (
            " ".join(brand_data.get("categories", [])) + " " +
            brand_data.get("summary", "")
        ).lower()

        for keyword, tag in keyword_to_tag_map.items():
            if keyword in search_text:
                tags_to_add.add(tag)

        # --- UPDATE LOGIC ---
        # Prepare the final update payload
        update_payload = {
            'regions': sorted(list(regions_to_add)), # Update the new array
            'tags': sorted(list(tags_to_add))      # Update the new array
        }
        
        # Only write to the database if there are actual changes
        if update_payload['regions'] != brand_data.get('regions', []) or \
           update_payload['tags'] != brand_data.get('tags', []):
            
            print(f"Updating '{brand_data.get('name', brand_id)}' -> Regions: {update_payload['regions']}, Tags: {update_payload['tags']}")
            doc.reference.update(update_payload)
            update_count += 1
        
    print("\n🎉 Enrichment complete!")
    print(f"Total documents updated: {update_count}")

if __name__ == "__main__":
    enrich_data()
