import json
from collections import Counter

with open('brands.json', 'r', encoding='utf-8') as f:
    brands = json.load(f)

# Check for duplicate IDs
ids = [brand['id'] for brand in brands]
duplicates = [id for id, count in Counter(ids).items() if count > 1]
print(f"Duplicate IDs: {duplicates}")

# Check for missing names or invalid entries
invalid = [brand for brand in brands if not brand.get('name') or not brand.get('id')]
print(f"Invalid entries: {len(invalid)}")

print(f"Total entries: {len(brands)}")
print(f"Valid entries: {len(brands) - len(invalid)}")
