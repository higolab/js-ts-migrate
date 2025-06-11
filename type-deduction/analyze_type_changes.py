import json
import sys
import re

if len(sys.argv) != 2:
	print("Usage: python classify_type_changes.py compare_result.json")
	sys.exit(1)

with open(sys.argv[1], "r") as f:
	data = json.load(f)

type_changes = data.get("type_changed", [])

function_type_changes = []
to_primitive_changes = []
to_any_array_changes = []
to_unknown_changes = []
to_empty_map_changes = []
generic_type_changes = []
object_property_type_changes = []
named_type_to_object_literal_changes = []
union_type_order_changes = []
generic_type_arguments_removed = []
to_object_literal_changes = []
other_type_changes = []

for entry in type_changes:
	orig = entry.get("original_type")
	new = entry.get("migrated_type")

	if not isinstance(orig, str) or not isinstance(new, str):
		other_type_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
		continue

	# 関数型が変化する場合
	if "=>" in orig and "=>" in new:
		function_type_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# プリミティブ型に変化する場合
	elif new.strip() in ["string", "number", "boolean", "bigint", "symbol" ,"null", "undefined", "string[]", "number[]", "boolean[]", "bigint[]", "symbol[]", "null[]", "undefined[]", "string[][]", "number[][]", "boolean[][]", "bigint[][]", "symbol[][]", "null[][]", "undefined[][]"]:
		to_primitive_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# anyの配列型に変化する場合
	elif new.strip() == "any[]" or new.strip() == "any[][]":
		to_any_array_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# unknownまたはunknown[] 型に変化する場合
	elif new.strip() in ["unknown", "unknown[]"]:
		to_unknown_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	#共用体型の順序が変化する場合
	elif (
	"|" in orig and "|" in new and
	set(part.strip() for part in orig.split("|")) == set(part.strip() for part in new.split("|")) and
	orig != new  # 順序が異なる
	):
		union_type_order_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# ジェネリクス型の型引数が削除される
	elif (
		re.match(r'^.*<.*>$', orig.strip()) and orig.split("<")[0].strip() == new.strip()
	):
		generic_type_arguments_removed.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# ジェネリクス型が変化する場合
	elif (
		re.match(r'^.*<.*>$', orig.strip()) and
		re.match(r'^.*<.*>$', new.strip())
	):
		generic_type_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# {} 型に変化する場合
	elif new.strip() == "{}":
		to_empty_map_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# オブジェクトのプロパティ型が変化する場合
	elif (
		orig.strip().startswith("{") and orig.strip().endswith("}")
		and new.strip().startswith("{") and new.strip().endswith("}")
	):
		object_property_type_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# 名前付き型からオブジェクト構造型に展開される場合
	elif (
		(not orig.strip().startswith("{")) and (not orig.strip().endswith("}")) and
		new.strip().startswith("{") and
		new.strip().endswith("}")
	):
		named_type_to_object_literal_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	# オブジェクトリテラル型(またはその配列)に展開される場合
	elif (
		"{" in new and "}" in new and  # migrated_type にオブジェクトリテラルあり
		"{" not in orig and "}" not in orig  # original_type にオブジェクト構造なし
	):
		to_object_literal_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})
	else:
		other_type_changes.append({
			"file": entry["file"],
			"name": entry["name"],
			"original_type": orig,
			"migrated_type": new
		})

# 出力結果（JSON形式）
result = {
	"summary": {
		"total_type_changed": len(type_changes),
		"function_type": len(function_type_changes),
		"to_primitive": len(to_primitive_changes),
		"to_any_array": len(to_any_array_changes),
		"to_unknown": len(to_unknown_changes),
		"union_order_changed": len(union_type_order_changes),
		"generic_type_arguments_removed": len(generic_type_arguments_removed),
		"generic_type_changed": len(generic_type_changes),
		"to_empty_map": len(to_empty_map_changes),
		"map_property_changed": len(object_property_type_changes),
		"named_type_to_object_literal": len(named_type_to_object_literal_changes),
		"to_object_literal": len(to_object_literal_changes),
		"other": len(other_type_changes),
	},
	"function_type_changes": function_type_changes,
	"to_primitive_changes": to_primitive_changes,
	"to_any_array_changes": to_any_array_changes,
	"to_unknown_changes": to_unknown_changes,
	"union_type_order_changes": union_type_order_changes,
	"generic_type_arguments_removed": generic_type_arguments_removed,
	"generic_type_changes": generic_type_changes,
	"to_empty_map_changes": to_empty_map_changes,
	"object_property_type_changes": object_property_type_changes,
	"named_type_to_object_literal_changes": named_type_to_object_literal_changes,
	"to_object_literal_changes": to_object_literal_changes,
	"other_type_changes": other_type_changes
	

}

print(json.dumps(result, indent=2, ensure_ascii=False))
