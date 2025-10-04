#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
This tests the fixes for the import issues found in the Docker logs.
"""
import sys
import traceback

def test_import(module_name, description):
    """Test importing a module and report results."""
    try:
        __import__(module_name)
        print(f"✅ {description}: Import successful")
        return True
    except Exception as e:
        print(f"❌ {description}: Import failed - {e}")
        traceback.print_exc()
        return False

def test_specific_imports():
    """Test specific imports that were failing."""
    print("Testing specific imports that were causing issues...")
    
    # Test the problematic import from routes/recommendations.py
    try:
        from services.logging_service import log_request
        print("✅ log_request function: Import successful")
        
        # Test that it's callable
        if callable(log_request):
            print("✅ log_request function: Is callable")
        else:
            print("❌ log_request function: Not callable")
            return False
            
    except Exception as e:
        print(f"❌ log_request function: Import failed - {e}")
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run all import tests."""
    print("🧪 Testing Smart Garden Planner Imports")
    print("=" * 50)
    
    tests = [
        ("models.database", "Database models"),
        ("models.schemas", "Pydantic schemas"),
        ("services.llm_service", "LLM service"),
        ("services.logging_service", "Logging service"),
        ("services.storage", "Storage service"),
        ("routes.recommendations", "Recommendations routes"),
    ]
    
    results = []
    
    # Test basic module imports
    for module, description in tests:
        results.append(test_import(module, description))
    
    print("\n" + "=" * 50)
    
    # Test specific problematic imports
    results.append(test_specific_imports())
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed!")
        return True
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)