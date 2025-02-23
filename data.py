import json
import os

# ✅ Correct folder path
folder_path = r"C:\Users\DELL\OneDrive\MINE\webapp-jhansi\zomato"

# ✅ Check if the folder exists
if not os.path.exists(folder_path):
    print(f"❌ Error: Folder '{folder_path}' not found!")
    exit()

# ✅ Get JSON files in the folder
json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

# ✅ Check if JSON files are found
if not json_files:
    print(f"❌ No JSON files found in '{folder_path}'!")
    exit()

print(f"🔍 Found {len(json_files)} JSON files. Merging data...")

merged_data = []

# ✅ Read and merge JSON files
for file in json_files:
    file_path = os.path.join(folder_path, file)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Extract restaurant records
            file_records = sum(len(entry["restaurants"]) for entry in data if "restaurants" in entry)
            print(f"📄 {file}: {file_records} records found.")

            # Add to merged data
            for entry in data:
                if "restaurants" in entry:
                    merged_data.extend([r["restaurant"] for r in entry["restaurants"]])
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON format in file '{file}'. Skipping...")

# ✅ Save merged data to merged.json
output_file = os.path.join(folder_path, "merged.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=4)

print(f"\n✅ Total records stored in merged.json: {len(merged_data)}")
print(f"🚀 Merged file saved at: {output_file}")
