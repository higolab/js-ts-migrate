import json
import sys

if len(sys.argv) != 3:
    print("Usage: python compare_types.py original.json migrated.json")
    sys.exit(1)

original_path = sys.argv[1]
migrated_path = sys.argv[2]

with open(original_path, "r") as f:
    original_data = json.load(f)

with open(migrated_path, "r") as f:
    migrated_data = json.load(f)

def index_by_file_and_name(data):
    return {
        (item["file"], item["name"]): item["type"]
        for item in data
    }

original_index = index_by_file_and_name(original_data)
migrated_index = index_by_file_and_name(migrated_data)

type_loss = []
type_change = []
new_entries = []
deleted_entries = []

# 1. Check type lost and changed
for key in original_index:
    orig_type = original_index[key]
    migrated_type = migrated_index.get(key)

    if migrated_type is None:
        deleted_entries.append((key[0], key[1], orig_type))
    elif migrated_type == "any" and orig_type != "any":
        type_loss.append((key[0], key[1], orig_type, migrated_type))
    elif orig_type != migrated_type and migrated_type != "any":
        type_change.append((key[0], key[1], orig_type, migrated_type))

# 2. Check for new entries
for key in migrated_index:
    if key not in original_index:
        new_entries.append((key[0], key[1], migrated_index[key]))

# === Report ===
def section(title, entries, formatter):
    print(f"\n=== {title} ({len(entries)}) ===")
    for entry in entries:
        print(formatter(*entry))

section("Type Lost (became 'any')", type_loss,
        lambda file, name, orig, new: f"{file}: {name} changed from {orig} → {new}")

section("Type Changed", type_change,
        lambda file, name, orig, new: f"{file}: {name} changed from {orig} → {new}")

section("New Entries in Migrated", new_entries,
        lambda file, name, typ: f"{file}: {name} added as type {typ}")

section("Deleted Entries", deleted_entries,
        lambda file, name, orig: f"{file}: {name} (original type: {orig})")

print(f"\nSummary:")
print(f"  Total in original : {len(original_index)}")
print(f"  Total in migrated : {len(migrated_index)}")
print(f"  Type lost         : {len(type_loss)}")
print(f"  Type changed      : {len(type_change)}")
print(f"  New entries       : {len(new_entries)}")
print(f"  Deleted entries   : {len(deleted_entries)}")
