import json
import os
import shutil

# Paths
# Move up one level from 'scripts/' to reach the project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_PATH = os.path.join(ROOT_DIR, "meta.json")
STATS_PATH = os.path.join(ROOT_DIR, "stats.json")
IMAGES_DIR = os.path.join(ROOT_DIR, "images")

def organize():
    if not os.path.exists(META_PATH):
        print(f"Error: {META_PATH} not found.")
        return

    with open(META_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get("items", [])
    print(f"Checking {len(items)} items from metadata...")

    moved_count = 0
    updated_count = 0
    ready_count = 0

    for item in items:
        old_name = item.get("file_name")
        
        if old_name.startswith("images/"):
            ready_count += 1
            continue
            
        category = item.get("category", "Uncategorized")
        folder_name = category.replace(" & ", "_").replace(" ", "_").lower()
        category_dir = os.path.join(IMAGES_DIR, folder_name)
        
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            
        old_path = os.path.join(ROOT_DIR, old_name)
        new_relative_path = f"images/{folder_name}/{old_name}"
        new_path = os.path.join(ROOT_DIR, new_relative_path)
        
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            item["file_name"] = new_relative_path
            moved_count += 1
            ready_count += 1
        else:
            if os.path.exists(new_path):
                item["file_name"] = new_relative_path
                updated_count += 1
                ready_count += 1

    # Save updated metadata
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    # GENERATE LIGHTWEIGHT STATS
    from datetime import datetime
    stats = {
        "total": len(items),
        "ready": ready_count,
        "percent": round((ready_count / len(items)) * 100, 2) if items else 0,
        "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Organize complete!")
    print(f"- Files physically moved: {moved_count}")
    print(f"- Metadata paths fixed: {updated_count}")
    print(f"- Stats saved to {STATS_PATH}")

if __name__ == "__main__":
    organize()
