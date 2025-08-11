"""
Azure Cognitive Search Helper Module

This module provides functions to interact with Azure Cognitive Search service
for indexing FAQ data and performing semantic search queries.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexer,
    IndexingParameters,
    IndexingSchedule
)
from azure.search.documents.indexes import SearchIndexClient
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureCognitiveSearchHelper:
    """Helper class for Azure Cognitive Search operations."""
    
    def __init__(self, endpoint: str, key: str, index_name: str = "faq-index"):
        """
        Initialize the Azure Cognitive Search helper.
        
        Args:
            endpoint (str): Azure Cognitive Search service endpoint
            key (str): Azure Cognitive Search API key
            index_name (str): Name of the search index
        """
        self.endpoint = endpoint
        self.key = key
        self.index_name = index_name
        self.credential = AzureKeyCredential(key)
        self.search_client = SearchClient(endpoint, index_name, self.credential)
        self.index_client = SearchIndexClient(endpoint, self.credential)
        
    def create_index(self) -> bool:
        """
        Create the FAQ search index with semantic search capabilities.
        
        Returns:
            bool: True if index created successfully, False otherwise
        """
        try:
            # Define the index schema
            index = SearchIndex(
                name=self.index_name,
                fields=[
                    SearchableField(name="id", type=SearchFieldDataType.String, key=True),
                    SearchableField(name="question", type=SearchFieldDataType.String, 
                                  searchable=True, filterable=True, sortable=True),
                    SearchableField(name="answer", type=SearchFieldDataType.String, 
                                  searchable=True, filterable=False, sortable=False),
                    SearchableField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                                  searchable=True, filterable=True, facetable=True),
                    SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset, 
                              filterable=True, sortable=True)
                ],
                semantic_settings=SemanticSettings(
                    configurations=[
                        SemanticConfiguration(
                            name="default",
                            prioritized_fields=SemanticField(
                                title_field=SemanticField(name="question"),
                                content_fields=[SemanticField(name="answer")],
                                keywords_fields=[SemanticField(name="tags")]
                            )
                        )
                    ]
                )
            )
            
            # Create the index
            result = self.index_client.create_or_update_index(index)
            logger.info(f"Index '{self.index_name}' created/updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            return False
    
    def upload_faqs_from_csv(self, csv_file_path: str) -> bool:
        """
        Upload FAQ data from a CSV file to the search index.
        
        Args:
            csv_file_path (str): Path to the CSV file containing FAQ data
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Prepare documents for upload
            documents = []
            for index, row in df.iterrows():
                doc = {
                    "id": f"faq_{index}",
                    "question": row["question"],
                    "answer": row["answer"],
                    "tags": row["tags"].split(",") if pd.notna(row["tags"]) else [],
                    "created_at": datetime.utcnow().isoformat() + "Z"
                }
                documents.append(doc)
            
            # Upload documents in batches
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                result = self.search_client.upload_documents(batch)
                
                # Check for errors
                failed_docs = [doc for doc in result if doc.succeeded is False]
                if failed_docs:
                    logger.warning(f"Failed to upload {len(failed_docs)} documents in batch {i//batch_size + 1}")
                
                logger.info(f"Uploaded batch {i//batch_size + 1} ({len(batch)} documents)")
            
            logger.info(f"Successfully uploaded {len(documents)} FAQ documents")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading FAQs: {str(e)}")
            return False
    
    def search_faqs(self, query: str, top: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant FAQs using semantic search.
        
        Args:
            query (str): Search query
            top (int): Number of top results to return
            
        Returns:
            List[Dict[str, Any]]: List of relevant FAQ documents
        """
        try:
            # Perform semantic search
            search_results = self.search_client.search(
                search_text=query,
                select=["id", "question", "answer", "tags"],
                top=top,
                query_type="semantic",
                query_language="en-us",
                semantic_configuration_name="default",
                query_caption="extractive",
                query_answer="extractive"
            )
            
            # Extract results
            results = []
            for result in search_results:
                doc = {
                    "id": result["id"],
                    "question": result["question"],
                    "answer": result["answer"],
                    "tags": result.get("tags", []),
                    "score": result.get("@search.score", 0),
                    "captions": result.get("@search.captions", []),
                    "answers": result.get("@search.answers", [])
                }
                results.append(doc)
            
            logger.info(f"Found {len(results)} relevant FAQs for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAQs: {str(e)}")
            return []
    
    def delete_index(self) -> bool:
        """
        Delete the search index.
        
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            self.index_client.delete_index(self.index_name)
            logger.info(f"Index '{self.index_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the search index.
        
        Returns:
            Dict[str, Any]: Index statistics
        """
        try:
            stats = self.index_client.get_index_statistics(self.index_name)
            return {
                "document_count": stats.document_count,
                "storage_size": stats.storage_size,
                "index_size": stats.index_size
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}

def create_search_helper() -> Optional[AzureCognitiveSearchHelper]:
    """
    Create an Azure Cognitive Search helper instance using environment variables.
    
    Returns:
        Optional[AzureCognitiveSearchHelper]: Helper instance or None if configuration is missing
    """
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "faq-index")
    
    if not endpoint or not key:
        logger.error("Azure Cognitive Search configuration missing. Please set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY")
        return None
    
    return AzureCognitiveSearchHelper(endpoint, key, index_name)
