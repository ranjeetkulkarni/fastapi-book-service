import sys
import os
from sqlalchemy import text

# --- FIX: Add 'src' to the system path so imports work ---
# This tells Python to treat the 'src' folder as a place to find modules
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Now we can import normally, just like the app does
from db.main import engine 

print("🗑️  Attempting to drop 'books' table...")

with engine.connect() as conn:
    # We use CASCADE to delete the table and any constraints linked to it
    conn.execute(text("DROP TABLE IF EXISTS books CASCADE;"))
    conn.commit()
    print("✅ Books table dropped successfully!")