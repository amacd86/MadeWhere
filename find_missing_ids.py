import json

with open('brands.json', 'r', encoding='utf-8') as f:
    brands = json.load(f)

# Get all actual IDs
actual_ids = [brand['id'] for brand in brands]
actual_ids.sort()

print(f"Total entries in JSON: {len(brands)}")
print(f"Highest ID: {max(actual_ids)}")
print(f"Lowest ID: {min(actual_ids)}")

# Find missing IDs in the sequence
expected_ids = set(range(1, 315))  # 1 to 314
actual_ids_set = set(actual_ids)
missing_ids = expected_ids - actual_ids_set

print(f"\nMissing IDs: {sorted(missing_ids)}")

# Show some context around missing IDs
for missing_id in sorted(missing_ids):
    print(f"\nMissing ID {missing_id}:")
    # Show brands before and after
    before = [b for b in brands if b['id'] == missing_id - 1]
    after = [b for b in brands if b['id'] == missing_id + 1]

    if before:
        print(f"  Before (ID {missing_id-1}): {before[0]['name']}")
    if after:
        print(f"  After (ID {missing_id+1}): {after[0]['name']}")
