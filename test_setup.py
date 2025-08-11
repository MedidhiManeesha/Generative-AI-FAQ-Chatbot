"""
Test Script for FAQ Chatbot Setup

This script tests the basic functionality of the Azure services
to ensure everything is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🔍 Testing Environment Variables...")
    
    required_vars = {
        "AZURE_SEARCH_ENDPOINT": "Azure Cognitive Search endpoint",
        "AZURE_SEARCH_KEY": "Azure Cognitive Search API key",
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint",
        "AZURE_OPENAI_KEY": "Azure OpenAI API key",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "Azure OpenAI deployment name"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} - Configured")
        else:
            print(f"❌ {var}: {description} - Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All environment variables are configured")
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("\n📦 Testing Module Imports...")
    
    try:
        import streamlit
        print("✅ streamlit - Imported successfully")
    except ImportError as e:
        print(f"❌ streamlit - Import failed: {e}")
        return False
    
    try:
        import azure.search.documents
        print("✅ azure.search.documents - Imported successfully")
    except ImportError as e:
        print(f"❌ azure.search.documents - Import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ openai - Imported successfully")
    except ImportError as e:
        print(f"❌ openai - Import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas - Imported successfully")
    except ImportError as e:
        print(f"❌ pandas - Import failed: {e}")
        return False
    
    try:
        from cognitive_search import create_search_helper
        print("✅ cognitive_search - Imported successfully")
    except ImportError as e:
        print(f"❌ cognitive_search - Import failed: {e}")
        return False
    
    try:
        from openai_helper import create_openai_helper
        print("✅ openai_helper - Imported successfully")
    except ImportError as e:
        print(f"❌ openai_helper - Import failed: {e}")
        return False
    
    print("✅ All modules imported successfully")
    return True

def test_azure_services():
    """Test Azure services connectivity."""
    print("\n🔗 Testing Azure Services...")
    
    try:
        from cognitive_search import create_search_helper
        search_helper = create_search_helper()
        
        if search_helper:
            print("✅ Azure Cognitive Search - Connected successfully")
            
            # Test index statistics
            stats = search_helper.get_index_stats()
            if stats:
                print(f"   📊 Index documents: {stats.get('document_count', 0)}")
            else:
                print("   ⚠️ Could not retrieve index statistics")
        else:
            print("❌ Azure Cognitive Search - Connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Azure Cognitive Search - Error: {e}")
        return False
    
    try:
        from openai_helper import create_openai_helper
        openai_helper = create_openai_helper()
        
        if openai_helper:
            print("✅ Azure OpenAI - Connected successfully")
        else:
            print("❌ Azure OpenAI - Connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Azure OpenAI - Error: {e}")
        return False
    
    return True

def test_data_files():
    """Test if required data files exist."""
    print("\n📁 Testing Data Files...")
    
    csv_path = "data/faqs.csv"
    if os.path.exists(csv_path):
        print(f"✅ {csv_path} - Found")
        
        # Check if file has content
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            print(f"   📊 CSV contains {len(df)} rows")
            print(f"   📋 Columns: {', '.join(df.columns)}")
        except Exception as e:
            print(f"   ⚠️ Could not read CSV file: {e}")
    else:
        print(f"❌ {csv_path} - Not found")
        return False
    
    return True

def main():
    """Main test function."""
    print("🧪 FAQ Chatbot Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Module Imports", test_imports),
        ("Azure Services", test_azure_services),
        ("Data Files", test_data_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("You can now run: streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
        print("Refer to the README.md for setup instructions.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
