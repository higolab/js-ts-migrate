import json
import sys
import os

if len(sys.argv) != 3:
    print("Usage: python compare_types.py original.json migrated.json")
    sys.exit(1)

original_path = sys.argv[1]
migrated_path = sys.argv[2]

with open(original_path, "r") as f:
    original_data = json.load(f)

with open(migrated_path, "r") as f:
    migrated_data = json.load(f)

def index_by_file_and_name_with_line(data):
    return {
        (item["file"], item["name"]): {
            "type": item["type"],
            "line": item.get("line"),
            "path": item.get("path")
        }
        for item in data
    }

original_index = index_by_file_and_name_with_line(original_data)
migrated_index = index_by_file_and_name_with_line(migrated_data)

type_loss = []
type_change = []

# 共通ファイル
common_files = set(file for file, _ in original_index.keys()) & set(file for file, _ in migrated_index.keys())

def get_code_context_by_line(file, orig_path, orig_line, mig_path, mig_line, lines_before=10, lines_after=10):
    def extract(path, line):
        try:
            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                lines = f.readlines()
            idx = line - 1
            start = max(0, idx - lines_before)
            end = min(len(lines), idx + lines_after)
            return "".join(lines[start:end]).rstrip()
        except Exception as e:
            return f"Error reading file: {e}"
    return extract(orig_path, orig_line), extract(mig_path, mig_line)

# 比較処理
for key in original_index:
    file, name = key
    if file not in common_files or key not in migrated_index:
        continue

    orig = original_index[key]
    mig = migrated_index[key]

    if orig["type"] != mig["type"]:
        context = get_code_context_by_line(file, orig["path"], orig["line"], mig["path"], mig["line"])
        entry = {
            "file": file,
            "name": name,
            "original_type": orig["type"],
            "migrated_type": mig["type"],
            "code_context": context
        }
        if orig["type"] != "any" and mig["type"] == "any":
            type_loss.append(entry)
        else:
            type_change.append(entry)

# === Markdown 出力 ===
def markdown_section(title, entries):
    if not entries:
        return
    print(f"# {title} ({len(entries)})\n")
    for e in entries:
        print(f"## `{e['file']}` - **{e['name']}**\n")
        print(f"- Original type: `{e['original_type']}`")
        print(f"- Migrated type: `{e['migrated_type']}`\n")
        print("### Original Code\n```ts")
        print(e["code_context"][0])
        print("```\n")
        print("### Migrated Code\n```ts")
        print(e["code_context"][1])
        print("```\n")

markdown_section("Type Lost (→ any)", type_loss)
markdown_section("Type Changed", type_change)
