"""
Test environment variables loading
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if all required variables are present
required_vars = [
    "EMBEDDING_AZURE_API_KEY",
    "EMBEDDING_AZURE_ENDPOINT", 
    "GENERATION_AZURE_API_KEY",
    "GENERATION_AZURE_ENDPOINT"
]

print("🔍 Checking environment variables...")
print("=" * 50)

all_present = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show first 10 and last 10 characters of API keys for security
        if "API_KEY" in var:
            display_value = f"{value[:10]}...{value[-10:]}"
        else:
            display_value = value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: Not found")
        all_present = False

print("=" * 50)
if all_present:
    print("🎉 All environment variables are properly set!")
    print("Your app should work on Streamlit Cloud once you add these as secrets.")
else:
    print("⚠️ Some environment variables are missing.")
