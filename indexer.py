\"\"\"
Locum Genius AI — Indexer
Creates a Gemini File Search Store and uploads all PDFs from 'Data For LGAI RAG'.
Run this ONCE to set up the knowledge base.
\"\"\"
import os
import sys
import time
import concurrent.futures
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

api_key = os.getenv(\"GOOGLE_API_KEY\")
if not api_key:
    raise ValueError(\"GOOGLE_API_KEY not found. Check your .env file in the project root.\")

client = genai.Client(api_key=api_key)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, \"Data For LGAI RAG\")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"config.txt\")


def create_store():
    print(\"Creating Locum Genius AI File Search Store...\")
    store = client.file_search_stores.create(
        config={\"display_name\": \"Locum Genius AI — UK Locum Guides\"}
    )
    print(f\"✅ Store created: {store.name}\")
    return store


def upload_single_file(file_path: str, store_name: str) -> bool:
    display_name = os.path.basename(file_path)
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f\"⬆️  Uploading: {display_name} ({size_mb:.1f} MB)...\")

    try:
        # Step 1: Upload to File API (Supports up to 2GB)
        file_obj = client.files.upload(
            file=file_path,
            config={\"display_name\": display_name}
        )
        file_name_resource = file_obj.name # Format: \"files/...\"
        
        # Step 2: Poll for file to be processed/Active
        waited = 0
        while True:
            file_obj = client.files.get(name=file_name_resource)
            if file_obj.state == \"ACTIVE\":
                break
            elif file_obj.state == \"FAILED\":
                print(f\"❌ File API FAIL for {display_name}: {getattr(file_obj, 'error', 'Unknown Error')}\")
                return False
            
            # Keep polling while in PROCESSING
            time.sleep(10) # 10s wait for large PDF processing
            waited += 10
            if waited % 60 == 0:
                print(f\"   ⏳ Processing {display_name} in File API... ({waited}s)\")
            
            if waited > 600: # 10 min timeout
                print(f\"❌ Timeout processing {display_name} after 10 mins.\")
                return False

        # Step 3: Add the active file to the File Search Store
        print(f\"   📦 Importing {display_name} into search store...\")
        operation = client.file_search_stores.import_file(
            file_search_store_name=store_name,
            file_name=file_name_resource
        )

        # Wait for the import operation to complete
        waited = 0
        while not operation.done:
            time.sleep(5)
            waited += 5
            try:
                operation = client.operations.get(operation)
            except Exception:
                pass
            if waited % 60 == 0:
                print(f\"   ⏳ Importing {display_name}... ({waited}s)\")

        print(f\"✅ Success: {display_name}\")
        return True

    except Exception as e:
        print(f\"❌ Error during {display_name}: {str(e)}\")
        import traceback
        traceback.print_exc()
        return False


def discover_files(data_dir: str) -> list[str]:
    \"\"\"Find all PDF and document files in the data directory.\"\"\"
    supported = {\".pdf\", \".docx\", \".txt\", \".md\"}
    found = []

    for root, _, files in os.walk(data_dir):
        for fname in sorted(files):
            if fname.startswith(\".\") or fname == \"desktop.ini\":
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext in supported:
                found.append(os.path.join(root, fname))

    return found


def main():
    print(\"=\" * 60)
    print(\"  LOCUM GENIUS AI — Knowledge Base Indexer\")
    print(\"=\" * 60)

    if not os.path.exists(DATA_DIR):
        print(f\"❌ Data directory not found:\\n   {DATA_DIR}\")
        sys.exit(1)

    files = discover_files(DATA_DIR)
    if not files:
        print(f\"❌ No supported files found in {DATA_DIR}\")
        sys.exit(1)

    print(f\"\\n📚 Found {len(files)} file(s) to upload:\")
    total_mb = 0
    for f in files:
        mb = os.path.getsize(f) / (1024 * 1024)
        total_mb += mb
        print(f\"   • {os.path.basename(f)} ({mb:.1f} MB)\")
    print(f\"\\n   Total: {total_mb:.1f} MB\\n\")

    # Create the store
    store = create_store()

    # Upload with parallel workers (limited to 3 so we don't saturate bandwidth)
    print(f\"\\n🚀 Starting parallel upload (3 workers)...\\n\")
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(upload_single_file, fp, store.name): fp
            for fp in files
        }
        results = {}
        for future in concurrent.futures.as_completed(futures):
            fp = futures[future]
            results[fp] = future.result()

    elapsed = time.time() - start_time
    success_count = sum(1 for v in results.values() if v)
    fail_count = len(results) - success_count

    print(\"\\n\" + \"=\" * 60)
    print(f\"  Upload Complete — {success_count}/{len(files)} succeeded ({elapsed:.0f}s)\")
    if fail_count:
        print(f\"  ⚠️  {fail_count} file(s) failed. Check errors above.\")
    print(\"=\" * 60)

    # Save the store name so app.py can use it
    with open(CONFIG_FILE, \"w\") as f:
        f.write(store.name)

    print(f\"\\n📝 Store name saved to: config.txt\")
    print(f\"   Store: {store.name}\")
    print(f\"\\n✅ Indexing complete! You can now run:\")
    print(f\"   streamlit run app.py\")


if __name__ == \"__main__\":
    main()
