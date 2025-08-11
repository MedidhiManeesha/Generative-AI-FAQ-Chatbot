"""
Setup Script for Azure Cognitive Search Index

This script helps you set up the Azure Cognitive Search index and upload FAQ data.
Run this script once to initialize your search service.
"""

import os
import sys
from dotenv import load_dotenv
from cognitive_search import create_search_helper

# Load environment variables
load_dotenv()

def main():
    """Main setup function."""
    print("🚀 Setting up Azure Cognitive Search Index for FAQ Chatbot")
    print("=" * 60)
    
    # Check environment variables
    required_vars = [
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    # Create search helper
    print("📡 Connecting to Azure Cognitive Search...")
    search_helper = create_search_helper()
    
    if not search_helper:
        print("❌ Failed to create search helper. Please check your configuration.")
        return False
    
    print("✅ Connected to Azure Cognitive Search")
    
    # Create index
    print("🔨 Creating search index...")
    if search_helper.create_index():
        print("✅ Search index created successfully")
    else:
        print("❌ Failed to create search index")
        return False
    
    # Upload FAQ data
    csv_path = "data/faqs.csv"
    if not os.path.exists(csv_path):
        print(f"❌ FAQ data file not found: {csv_path}")
        print("Please ensure the data/faqs.csv file exists.")
        return False
    
    print("📤 Uploading FAQ data...")
    if search_helper.upload_faqs_from_csv(csv_path):
        print("✅ FAQ data uploaded successfully")
    else:
        print("❌ Failed to upload FAQ data")
        return False
    
    # Display index statistics
    print("\n📊 Index Statistics:")
    stats = search_helper.get_index_stats()
    if stats:
        print(f"   Documents: {stats.get('document_count', 0)}")
        print(f"   Storage Size: {stats.get('storage_size', 0)} bytes")
        print(f"   Index Size: {stats.get('index_size', 0)} bytes")
    
    print("\n🎉 Setup completed successfully!")
    print("You can now run the Streamlit app with: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
