# SQLite3 version fix for Streamlit Cloud deployment
# This script handles the ChromaDB SQLite3 version compatibility issue

import sys

# Try to use pysqlite3-binary instead of the system sqlite3
try:
    __import__('pysqlite3')
    import pysqlite3 as sqlite3
    sys.modules['sqlite3'] = pysqlite3
    print("✅ Using pysqlite3-binary for ChromaDB compatibility")
except ImportError:
    # Fallback to system sqlite3 if pysqlite3-binary is not available
    import sqlite3
    print(f"⚠️ Using system sqlite3 version: {sqlite3.sqlite_version}")
    print("ChromaDB may not work properly with older SQLite versions")
