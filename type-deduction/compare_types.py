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
            "line": item.get("line", None),
            "path": item.get("path", None)
        }
        for item in data
    }

original_index = index_by_file_and_name_with_line(original_data)
migrated_index = index_by_file_and_name_with_line(migrated_data)

type_loss = []
type_change = []
unchanged_any = []
unchanged_not_any = []
new_entries = []
deleted_entries = []

# ファイル名の共通集合を取得
original_files = set(file for file, _ in original_index.keys())
migrated_files = set(file for file, _ in migrated_index.keys())
common_files = original_files & migrated_files
new_files = migrated_files - original_files
deleted_files = original_files - migrated_files

# 共通ファイル内のエントリ数カウント
common_original_count = sum(1 for (file, _) in original_index if file in common_files)
common_migrated_count = sum(1 for (file, _) in migrated_index if file in common_files)

def get_code_context_by_line(file_name,original_path,original_line,migrated_path,migrated_line, lines_before=10, lines_after=10):
    try:
        ans=[]
        original_path=original_path+ file_name
        with open(original_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        i = original_line - 1  # line number is 1-based
        start = max(0, i - lines_before)
        end = min(len(lines), i + lines_after)
        ans.append([l.rstrip() for l in lines[start:end]])
        
        migrated_path=migrated_path+ file_name
        with open(migrated_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        i = migrated_line - 1  # line number is 1-based
        start = max(0, i - lines_before)
        end = min(len(lines), i + lines_after)
        ans.append([l.rstrip() for l in lines[start:end]])
        return ans
    except Exception as e:
        return [f"Error reading file: {e}"]

# 共通ファイルのみ対象に比較
for key in original_index:
    file, name = key
    if file not in common_files:
        continue

    if key not in migrated_index:
        deleted_entries.append({
            "file": file,
            "name": name,
            "original_type": original_index[key]["type"]
        })
        continue

    orig_type = original_index[key]["type"]
    orig_line = original_index[key]["line"]
    orig_path= original_index[key]["path"]
    migrated_type = migrated_index[key]["type"]
    migrated_line = migrated_index[key]["line"]
    migrated_path = migrated_index[key]["path"]

    if migrated_type == "any" and orig_type != "any":
        code_context = get_code_context_by_line(file, orig_path, orig_line, migrated_path, migrated_line)
        type_loss.append({
            "file": file,
            "name": name,
            "original_type": orig_type,
            "code_context": code_context
        })
    elif orig_type != migrated_type and migrated_type != "any":
        code_context = get_code_context_by_line(file, orig_path, orig_line, migrated_path, migrated_line)
        type_change.append({
            "file": file,
            "name": name,
            "original_type": orig_type,
            "migrated_type": migrated_type,
            "code_context": code_context
        })
    elif orig_type == "any" and migrated_type == "any":
        unchanged_any.append({
            "file": file,
            "name": name
        })
    elif orig_type == migrated_type:
        unchanged_not_any.append({
            "file": file,
            "name": name,
            "type": orig_type
        })

# new_entries: 共通ファイルに含まれる新しい名前のみ
for key in migrated_index:
    file, name = key
    if key not in original_index and file in common_files:
        new_entries.append({
            "file": file,
            "name": name,
            "migrated_type": migrated_index[key]["type"]
        })

# 出力
result = {
    "summary": {
        "total_original": common_original_count,
        "total_migrated": common_migrated_count,
        "type_lost": len(type_loss),
        "type_changed": len(type_change),
        "unchanged_any": len(unchanged_any),
        "unchanged_not_any": len(unchanged_not_any),
        "new_entries": len(new_entries),
        "deleted_entries": len(deleted_entries),
        "common_files": len(common_files),
        "new_files": len(new_files),
        "deleted_files": len(deleted_files)
    },
    "type_lost": type_loss,
    "type_changed": type_change,
    "unchanged_any": unchanged_any,
    "unchanged_not_any": unchanged_not_any,
    "new_entries": new_entries,
    "deleted_entries": deleted_entries
}

print(json.dumps(result, indent=2, ensure_ascii=False))
