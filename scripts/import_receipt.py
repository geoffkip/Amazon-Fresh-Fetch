import sqlite3
import re
import os

# --- PASTE PURCHASE HISTORY HERE ---
RAW_DATA = """
Items in your order 
"""

def import_data():
    # 1. Connect to Database
    db_path = "agent_data.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Ensure the table exists
    c.execute('''CREATE TABLE IF NOT EXISTS purchase_history 
                 (item_name TEXT PRIMARY KEY, count INTEGER DEFAULT 1)''')

    # 2. Parse the Text
    # Remove header junk and newlines to make one long string
    clean_text = RAW_DATA.replace("Items in your order", "").replace("QuantityWeightTotal", "").replace("\n", " ")
    
    # Split by the price pattern: Number + $ + Digits + . + Digits
    # This regex handles cases like "1$1.73" or "2$4.98"
    # (\d+\$\d+\.\d+) captures the price block
    tokens = re.split(r'(\d+\$\d+\.\d+)', clean_text)
    
    items_found = []
    
    for token in tokens:
        token = token.strip()
        # Filter out prices ($) and empty strings
        if not token or "$" in token:
            continue
        
        # Clean up the item name
        # The quantity number (e.g. '1' or '2') is usually stuck to the end of the name
        # Example: "Peanut Butter1" -> "Peanut Butter"
        # Also handle the "Weight adjusted" text that appears in meat orders
        item_name = re.sub(r'Weight adjusted.*', '', token) # Remove weight notes
        item_name = re.sub(r'\d+$', '', item_name).strip() # Remove trailing quantity digit
        
        if len(item_name) > 3: 
            items_found.append(item_name)

    # 3. Insert into DB
    print(f"🔍 Found {len(items_found)} items.")
    count_new = 0
    
    for item in items_found:
        print(f"   -> {item}")
        try:
            # Upsert: Add 1 to count if exists, else insert
            c.execute("""
                INSERT INTO purchase_history (item_name, count) 
                VALUES (?, 1) 
                ON CONFLICT(item_name) DO UPDATE SET count = count + 1
            """, (item,))
            count_new += 1
        except Exception as e:
            print(f"Error saving {item}: {e}")

    conn.commit()
    conn.close()
    print("-" * 30)
    print(f"✅ Successfully trained AI on {count_new} items.")

if __name__ == "__main__":
    import_data()