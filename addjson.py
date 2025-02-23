import json
import os
from supabase import create_client, Client

# ✅ Supabase Credentials
SUPABASE_URL = "https://svbwfqaiewfnhcdyijlw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2YndmcWFpZXdmbmhjZHlpamx3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAyMDY2NjgsImV4cCI6MjA1NTc4MjY2OH0.k_xR8vAxG8jFsCgIzwJMPEBNONX2cWt5Dwr6kF97GDc"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Path to merged JSON file
folder_path = r"C:\Users\DELL\OneDrive\MINE\webapp-jhansi\zomato"
merged_file = os.path.join(folder_path, "merged.json")

# ✅ Load the merged JSON data
with open(merged_file, "r", encoding="utf-8") as f:
    merged_data = json.load(f)

print(f"✅ Total records before filtering: {len(merged_data)}")

# ✅ Remove "R" column & track unique IDs
unique_records = []
seen_ids = set()

for record in merged_data:
    if "R" in record:
        del record["R"]  # Remove unwanted "R" field

    record_id = record.get("id")

    if record_id and record_id not in seen_ids:
        seen_ids.add(record_id)
        unique_records.append(record)

print(f"✅ Total unique records to insert: {len(unique_records)}")

# ✅ Batch insert to avoid Supabase size limits
batch_size = 100  # Adjust if needed
for i in range(0, len(unique_records), batch_size):
    batch = unique_records[i : i + batch_size]
    response = supabase.table("zomato_full_data").upsert(batch).execute()

    # ✅ Handle errors properly
    if isinstance(response, dict) and "error" in response:
        print(f"⚠️ Error in batch {i}-{i + batch_size}: {response['error']}")
    else:
        print(f"✅ Inserted batch {i}-{i + batch_size}, records inserted: {len(batch)}")

print("🚀 Data upload complete!")
