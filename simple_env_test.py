#!/usr/bin/env python3
import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    print("✅ Loaded .env file")
except ImportError as e:
    print(f"⚠️  python-dotenv not available: {e}")
except Exception as e:
    print(f"❌ Error loading .env: {e}")

# Check environment variables
print(f"GENAI_API_KEY: {os.getenv('GENAI_API_KEY', 'NOT_SET')}")
print(f"GENAI_ENDPOINT: {os.getenv('GENAI_ENDPOINT', 'NOT_SET')}")

# Try to import the service
sys.path.append('backend')
try:
    from services.llm_service import llm_service
    print(f"✅ Service imported successfully")
    print(f"Service enabled: {llm_service.enabled}")
    print(f"API Key present: {bool(llm_service.api_key)}")
    print(f"Endpoint: {llm_service.endpoint}")
except Exception as e:
    print(f"❌ Error importing service: {e}")
    import traceback
    traceback.print_exc()