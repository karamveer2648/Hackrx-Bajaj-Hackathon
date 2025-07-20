"""
Test script to verify SQLite3 compatibility fix for ChromaDB
Run this to check if the fix works before deploying
"""

# SQLite3 compatibility fix for ChromaDB on Streamlit Cloud
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("✅ Successfully applied pysqlite3 fix")
except ImportError:
    print("⚠️ pysqlite3-binary not found, using system sqlite3")

import sqlite3
print(f"SQLite version: {sqlite3.sqlite_version}")

try:
    import chromadb
    print("✅ ChromaDB import successful")
    
    # Test basic ChromaDB functionality
    client = chromadb.Client()
    print("✅ ChromaDB client creation successful")
    print("🎉 SQLite3 fix is working correctly!")
    
except Exception as e:
    print(f"❌ ChromaDB error: {e}")
    print("The fix may need additional adjustments")
