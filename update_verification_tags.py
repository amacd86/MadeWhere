# update_verification_tags.py
# A one-time script to add a 'source_verified' or 'brand_reported' tag
# to all brand documents based on prior research.

import firebase_admin
from firebase_admin import credentials, firestore

# --- SETUP ---
try:
    cred = credentials.Certificate("serviceAccountKey_firebase.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Successfully authenticated and connected to Firestore.")
except Exception as e:
    print(f"🔥 Authentication failed: {e}")
    exit()

# ==============================================================================
# AI RESEARCH RESULTS
# This dictionary contains the verification status for each brand.
# ==============================================================================
brand_verification_updates = {
    # ... (full dictionary as provided in the prompt) ...
    "Floyd": "source_verified", "Herman Miller": "source_verified", "Steelcase": "source_verified",
    "La-Z-Boy": "source_verified", "Vaughan-Bassett": "source_verified", "L.L.Bean": "source_verified",
    "New Balance (Made in USA)": "source_verified", "American Giant": "source_verified", "Estwing": "source_verified",
    "Darn Tough Vermont": "source_verified", "Wiffle Ball, Inc.": "source_verified", "Origin Maine": "source_verified",
    "Vermont Flannel Company": "source_verified", "New England Shirt Company": "source_verified", "All American Clothing Co.": "source_verified",
    "Gitman Bros.": "source_verified", "Bondhus": "source_verified", "Wilde Tool": "source_verified",
    "Wright Tool": "source_verified", "Klein Tools": "source_verified", "Marshalltown": "source_verified",
    "Lucchese Bootmaker": "source_verified", "Mystery Ranch": "source_verified", "Oomingmak": "source_verified",
    "West Paw": "source_verified", "Good To-Go": "source_verified", "Liberty Graphics": "source_verified",
    "Brant & Cochran": "source_verified", "Rancourt & Co.": "source_verified", "Quoddy": "source_verified",
    "Fox Family Chips": "source_verified", "Easymoc": "source_verified", "Flowfold": "source_verified",
    "Turtle Fur": "source_verified", "Johnson Woolen Mills": "source_verified", "Burgeon Outdoor": "source_verified",
    "Bailey Works": "source_verified", "LupinePet": "source_verified", "Limmer Boots": "source_verified",
    "Ragged Mountain Equipment": "source_verified", "Stonewall Kitchen": "source_verified", "Teddy Peanut Butter": "source_verified",
    "Grillo's Pickles": "source_verified", "Cape Cod Potato Chips": "source_verified", "Yankee Candle": "source_verified",
    "Ocean Spray": "source_verified", "Paul Component Engineering": "source_verified", "Chris King Precision Components": "source_verified",
    "Moots": "source_verified", "Lynskey Performance": "source_verified", "HED Cycling Products": "source_verified",
    "Franklin Sports": "source_verified", "Taco Comfort Solutions": "source_verified", "White Industries": "source_verified",
    "Lodge Cast Iron": "source_verified", "Leatherman": "source_verified", "KitchenAid": "source_verified",
    "Zippo": "source_verified", "Corningware": "source_verified", "Pyrex": "source_verified", "Weber Grills": "source_verified",
    "Filson": "source_verified", "Schott NYC": "source_verified", "Libman": "source_verified", "Tervis": "source_verified",
    "Vermont Teddy Bear": "source_verified", "Green Toys": "source_verified", "Red Wing Heritage": "source_verified",
    "Channellock": "source_verified", "Case Knives": "source_verified", "Louisville Slugger": "source_verified",
    "Okabashi Brands": "source_verified", "Smithey Ironware Co.": "source_verified", "Diamond Brand Gear": "source_verified",
    "Red Land Cotton": "source_verified", "Zkano": "source_verified", "Cheerwine": "source_verified",
    "Mt. Olive Pickle Company": "source_verified", "Texas Pete": "source_verified", "MoonPie": "source_verified",
    "American Leather": "source_verified", "Buck Knives": "source_verified", "Gibson Guitar": "source_verified",
    "Rite in the Rain": "source_verified", "Stormy Kromer": "source_verified", "Wigwam Socks": "source_verified",
    "Anchor Hocking": "source_verified", "Simms Fishing Products": "source_verified", "Allen Edmonds": "source_verified",
    "General Electric (Appliances)": "source_verified", "White Oak Pastures": "source_verified", "Thistle Farms": "source_verified",
    "Holtz Leather Co.": "source_verified", "Alabama Sawyer": "source_verified", "Emily G's": "source_verified",
    "Orca Coolers": "source_verified", "Cathead Distillery": "source_verified", "Blue Delta Jeans": "source_verified",
    "Benchmade Knife Company": "source_verified", "Tough Traveler": "source_verified", "Hinkle Chair Company": "source_verified",
    "Flint and Tinder": "source_verified", "Jacobsen Salt Co.": "source_verified", "Schoolhouse Electric": "source_verified",
    "Duluth Pack": "source_verified", "Faribault Woolen Mill Co.": "source_verified", "Epicurean": "source_verified",
    "Missouri Meerschaum": "source_verified", "Vollrath Company": "source_verified", "Bully Tools": "source_verified",
    "Council Tool": "source_verified", "Warwood Tool": "source_verified", "Carhartt (Made in USA)": "source_verified",
    "Annin Flagmakers": "source_verified", "Nordic Ware": "source_verified", "Topo Designs": "source_verified",
    "Melanzana": "source_verified", "Duckworth": "source_verified", "Maglite": "source_verified", "SureFire": "source_verified",
    "Heath Ceramics": "source_verified", "Rickshaw Bagworks": "source_verified", "Danner Boots": "source_verified",
    "Pendleton Woolen Mills": "source_verified", "Feathered Friends": "source_verified", "Kershaw Knives": "source_verified",
    "Beyond Clothing": "source_verified", "Crescent Down Works": "source_verified", "Exotac": "source_verified",
    "Vortex Optics": "source_verified", "Head Country Bar-B-Q": "source_verified", "Propper": "source_verified",
    "Volpi Foods": "source_verified", "Community Coffee": "source_verified", "Abita Brewing Company": "source_verified",
    "WeatherTech": "source_verified", "HammerHead Moles": "source_verified", "Carmex": "source_verified",
    "Bison Coolers": "source_verified", "Stetson": "source_verified", "Martin Guitar": "source_verified",
    "Mack Trucks": "source_verified", "Harley-Davidson (York)": "source_verified", "Yuengling": "source_verified",
    "Utz Quality Foods": "source_verified", "Hershey's": "source_verified", "Peeps": "source_verified",
    "Hubbard Peanut Company": "source_verified", "Homer Laughlin China": "source_verified", "Blenko Glass Company": "source_verified",
    "J.Q. Dickinson Salt-Works": "source_verified", "Four Roses Bourbon": "source_verified", "Grado Labs": "source_verified",
    "Hanky Panky": "source_verified", "Marble King": "source_verified", "Dogfish Head": "source_verified",
    "Mag Instrument": "source_verified", "Work Sharp": "source_verified", "Seek Outside": "source_verified",
    "Enlightened Equipment": "source_verified", "Tanka Bar": "source_verified", "Montana Watch Company": "source_verified",
    "Mountain Meadow Wool Mill": "source_verified", "Maven Outdoor Equipment": "source_verified", "Yoder Smokers": "source_verified",
    "Shawnee Milling Company": "source_verified", "The Roasterie": "source_verified", "Daisy Outdoor Products": "source_verified",
    "War Eagle Boats": "source_verified", "Savage Arms": "source_verified", "Blueridge Chair Works": "source_verified",
    "Shinola": "source_verified", "Wood-Mizer": "source_verified", "Fiesta Tableware": "source_verified",

    # Reported Brands (Claims are primarily from the brand itself or are ambiguous/globally sourced)
    "Room & Board": "brand_reported", "Polywood": "brand_reported", "West Elm": "brand_reported",
    "Ashley Furniture": "brand_reported", "IKEA": "brand_reported", "Tekton": "brand_reported",
    "Boll & Branch": "brand_reported", "NEMO Equipment": "brand_reported", "Ben & Jerry's": "brand_reported",
    "Faygo": "brand_reported", "Better Made": "brand_reported", "Bertman Original Ball Park Mustard": "brand_reported",
    "Polar Beverages": "brand_reported", "Moxie": "brand_reported", "Hasbro": "brand_reported",
    "Kona Bikes": "brand_reported", "Salsa Cycles": "brand_reported", "Gibson": "brand_reported",
    "Igloo Coolers": "brand_reported", "Wilson Sporting Goods": "brand_reported", "Goruck": "brand_reported",
    "YETI": "brand_reported", "Crayola": "brand_reported", "3M": "brand_reported", "King Koil": "brand_reported",
    "Duke Cannon Supply Co.": "brand_reported", "Calphalon": "brand_reported", "O'Keeffe's Company": "brand_reported",
    "Burt's Bees": "brand_reported", "The Honest Company": "brand_reported", "Mud Pie": "brand_reported",
    "CreekKooler": "brand_reported", "Lamons": "brand_reported", "Lily & Lottie": "brand_reported",
    "Native Creole": "brand_reported", "Cajun Spoon": "brand_reported", "Makr": "brand_reported",
    "The New Primal": "brand_reported", "Lowcountry Kettle": "brand_reported", "Bulls Bay Saltworks": "brand_reported",
    "HVNLY": "brand_reported", "Ethel M Chocolates": "source_verified", "Swoon": "brand_reported", "Scandivanian": "brand_reported",
    "Amana Furniture & Clock Shop": "source_verified", "5.11 Tactical": "brand_reported", "Ekornes (Stressless)": "brand_reported",
    "Frye Company": "brand_reported", "Kelty": "brand_reported", "Faribault Foods": "brand_reported",
    "Tony Chachere's": "source_verified", "Black Rifle Coffee Company": "brand_reported", "Gerber Gear": "brand_reported",
    "Litespeed Bicycles": "source_verified", "Cabela's": "brand_reported", "Coleman Company": "brand_reported",
    "Brahmin": "brand_reported", "Peterboro Basket Company": "brand_reported", "Smartwool": "brand_reported",
    "Black Diamond Equipment": "brand_reported", "Goal Zero": "brand_reported", "Cotopaxi": "brand_reported",
    "Patagonia": "brand_reported", "The North Face (Backpacks)": "brand_reported", "Cascade Designs": "brand_reported",
    "Stasher": "brand_reported", "Klean Kanteen": "brand_reported", "Hydro Flask": "brand_reported",
    "MelroseCo": "brand_reported", "Bismarck Mandan CVB": "brand_reported", "Dakota Layers": "brand_reported",
    "Prairie Berry Winery": "source_verified", "Montana Mex": "brand_reported", "Melvin Brewing": "source_verified",
    "Dorothy Lynch Home Style Dressing": "source_verified", "Poppytalk": "brand_reported", "Braum's": "brand_reported",
    "Rose Bud Foulks": "brand_reported", "Grapette": "brand_reported", "Zapp's Potato Chips": "source_verified",
    "Tony's Seafood": "source_verified", "Duck Commander": "brand_reported", "Grown As* Cereal": "brand_reported",
    "Snyder's of Hanover": "brand_reported", "Campbell's Soup": "brand_reported", "Dr. Scholl's (Insoles)": "brand_reported",
    "Corle + Hand": "brand_reported", "MacKenzie-Childs": "brand_reported", "Gorham Silver": "brand_reported",
    "Doggone Good": "brand_reported", "Iglidur": "brand_reported", "Chaco": "brand_reported",
    "Kingston": "brand_reported", "Scosche Industries": "brand_reported", "The Original Muck Boot Company": "brand_reported",
    "Outdoor Research": "brand_reported", "Boyd's Coffee": "brand_reported", "DeMarini Sports": "source_verified",
    "Klim": "brand_reported", "Proof Eyewear": "brand_reported", "Purple Mattress": "source_verified",
    "Stance": "brand_reported", "TRUCK Gloves": "brand_reported", "Scheels": "brand_reported",
    "Dakota Angler": "brand_reported", "Alps OutdoorZ": "brand_reported", "Traeger Grills": "brand_reported",
    "Vitamix": "source_verified", "Able Brewing Equipment": "brand_reported", "Showers Pass": "brand_reported",
    "CamelBak": "brand_reported", "GSI Outdoors": "brand_reported", "Chrome Industries": "brand_reported",
    "Kialoa Paddles": "source_verified", "Bison Booties": "brand_reported", "Pride of Dakota": "brand_reported",
    "Dakotah Inc": "brand_reported", "Bulldoggers": "brand_reported", "Heartland Mill": "source_verified",
    "The Pasta House Co.": "brand_reported", "Slumberkins": "brand_reported", "Lawn-Boy": "brand_reported",
    "Vera Bradley": "brand_reported", "American Expedition Vehicles": "source_verified", "Best Chairs Storytime Series": "brand_reported",
    "J.A. Henckels International": "brand_reported", "Alex and Ani": "brand_reported", "Timberland": "brand_reported",
    "Serotta": "brand_reported", "La Sportiva (Rebuilds)": "source_verified", "Frye Boots (Arkansas)": "brand_reported",
    "The Pasta House Co.": "brand_reported", "Chaco (MI)": "source_verified", "Filson (ID)": "source_verified"
}

# ==============================================================================
# SCRIPT LOGIC (No editing needed below this line)
# ==============================================================================

def update_brand_tags():
    """
    Loops through all brands in Firestore and updates their tags array
    with the verification status from the dictionary above.
    """
    brands_ref = db.collection('brands')
    docs = brands_ref.stream()

    print("\n🚀 Starting tag update process...")
    update_count = 0
    brands_not_found = []

    all_brand_docs = {doc.to_dict().get('name'): doc for doc in docs}

    for brand_name, verification_tag in brand_verification_updates.items():
        if brand_name in all_brand_docs:
            doc = all_brand_docs[brand_name]
            brand_data = doc.to_dict()
            
            # Start with existing tags to preserve them
            existing_tags = set(brand_data.get('tags', []))
            
            # Remove any old verification tags to prevent conflicts
            existing_tags.discard('source_verified')
            existing_tags.discard('brand_reported')
            
            # Add the new, correct verification tag
            existing_tags.add(verification_tag)
            
            # Prepare the final, sorted list of tags
            new_tags_list = sorted(list(existing_tags))

            # Only write to the database if there's a change
            if new_tags_list != sorted(brand_data.get('tags', [])):
                print(f"Updating '{brand_name}' -> New Tags: {new_tags_list}")
                doc.reference.update({'tags': new_tags_list})
                update_count += 1
        else:
            brands_not_found.append(brand_name)

    print("\n🎉 Tag update complete!")
    print(f"Total documents updated: {update_count}")
    if brands_not_found:
        print("\n⚠️ The following brands from the update list were not found in the database:")
        for name in brands_not_found:
            print(f"- {name}")

if __name__ == "__main__":
    update_brand_tags()
