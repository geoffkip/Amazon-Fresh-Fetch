import sqlite3
import pandas as pd
import os

DB_NAME = "../agent_data.db"

def view_database():
    if not os.path.exists(DB_NAME):
        print(f"❌ Error: Database '{DB_NAME}' not found.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- 1. CHECK TABLES ---
    print(f"\n🗄️  Database: {DB_NAME}")
    print("=" * 40)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables found: {[t[0] for t in tables]}")

    # --- 2. VIEW PURCHASE HISTORY ---
    print("\n🛒 Table: purchase_history (Top 20)")
    print("-" * 40)
    try:
        # Using pandas for a nice readable table output
        df_history = pd.read_sql_query("SELECT * FROM purchase_history ORDER BY count DESC LIMIT 50", conn)
        if not df_history.empty:
            print(df_history)
        else:
            print("(No data found)")
    except Exception as e:
        print(f"Could not read purchase_history: {e}")

    # --- 3. VIEW SETTINGS ---
    print("\n⚙️  Table: settings")
    print("-" * 40)
    try:
        df_settings = pd.read_sql_query("SELECT * FROM settings", conn)
        if not df_settings.empty:
            print(df_settings)
        else:
            print("(No settings saved yet)")
    except Exception as e:
        print(f"Could not read settings: {e}")

    # --- 4. VIEW MEAL PLANS (Summary) ---
    print("\n📅 Table: meal_plans (Last 5)")
    print("-" * 40)
    try:
        # Select specific columns to avoid printing giant JSON blobs
        query = "SELECT id, date, prompt, length(shopping_list) as list_size FROM meal_plans ORDER BY id DESC LIMIT 5"
        df_plans = pd.read_sql_query(query, conn)
        if not df_plans.empty:
            print(df_plans)
        else:
            print("(No meal plans saved yet)")
    except Exception as e:
        print(f"Could not read meal_plans: {e}")

    conn.close()

if __name__ == "__main__":
    view_database()