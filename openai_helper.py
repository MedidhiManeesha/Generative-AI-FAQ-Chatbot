"""
Azure OpenAI Helper Module

This module provides functions to interact with Azure OpenAI Service
for generating intelligent responses based on FAQ search results.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureOpenAIHelper:
    """Helper class for Azure OpenAI operations."""
    
    def __init__(self, endpoint: str, key: str, deployment_name: str, api_version: str = "2023-12-01-preview"):
        """
        Initialize the Azure OpenAI helper.
        
        Args:
            endpoint (str): Azure OpenAI service endpoint
            key (str): Azure OpenAI API key
            deployment_name (str): Name of the deployed model
            api_version (str): API version to use
        """
        self.endpoint = endpoint
        self.key = key
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version=api_version
        )
    
    def generate_answer(self, user_query: str, relevant_faqs: List[Dict[str, Any]]) -> str:
        """
        Generate an intelligent answer based on user query and relevant FAQs.
        
        Args:
            user_query (str): The user's question
            relevant_faqs (List[Dict[str, Any]]): List of relevant FAQ documents
            
        Returns:
            str: Generated answer
        """
        try:
            # Prepare context from relevant FAQs
            context = self._prepare_context(relevant_faqs)
            
            # Create system prompt
            system_prompt = """You are an intelligent FAQ assistant powered by Azure OpenAI. Your role is to:

1. Analyze the user's question and the provided relevant FAQ information
2. Generate a comprehensive, accurate, and helpful answer
3. Use the FAQ information as your primary source of truth
4. If the FAQ information doesn't fully address the question, acknowledge this and provide the best possible answer based on available information
5. Structure your response clearly and professionally
6. If multiple FAQs are relevant, synthesize the information coherently

Always be helpful, accurate, and professional in your responses."""

            # Create user message
            user_message = f"""User Question: {user_query}

Relevant FAQ Information:
{context}

Please provide a comprehensive answer based on the above information."""

            # Generate response
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.3,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer for query: '{user_query[:50]}...'")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error while generating your answer. Please try again or rephrase your question."
    
    def _prepare_context(self, relevant_faqs: List[Dict[str, Any]]) -> str:
        """
        Prepare context string from relevant FAQ documents.
        
        Args:
            relevant_faqs (List[Dict[str, Any]]): List of relevant FAQ documents
            
        Returns:
            str: Formatted context string
        """
        context_parts = []
        
        for i, faq in enumerate(relevant_faqs, 1):
            question = faq.get("question", "")
            answer = faq.get("answer", "")
            tags = faq.get("tags", [])
            score = faq.get("score", 0)
            
            # Format tags
            tags_str = ", ".join(tags) if tags else "No tags"
            
            # Add FAQ to context
            faq_context = f"""FAQ {i} (Relevance Score: {score:.3f}):
Question: {question}
Answer: {answer}
Tags: {tags_str}
---"""
            
            context_parts.append(faq_context)
        
        return "\n".join(context_parts)
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the intent and category of a user query.
        
        Args:
            query (str): User's query
            
        Returns:
            Dict[str, Any]: Analysis results including intent and category
        """
        try:
            system_prompt = """Analyze the user's query and provide:
1. Intent: What the user is trying to accomplish
2. Category: The main topic area (e.g., setup, troubleshooting, pricing, etc.)
3. Keywords: Important terms that should be used for search
4. Complexity: Simple, Medium, or Complex

Respond in JSON format:
{
    "intent": "string",
    "category": "string", 
    "keywords": ["string"],
    "complexity": "string"
}"""

            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            analysis = json.loads(result_text)
            
            logger.info(f"Query analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing query intent: {str(e)}")
            return {
                "intent": "general_inquiry",
                "category": "general",
                "keywords": query.split(),
                "complexity": "medium"
            }
    
    def suggest_related_questions(self, user_query: str, relevant_faqs: List[Dict[str, Any]]) -> List[str]:
        """
        Suggest related questions based on the user's query and relevant FAQs.
        
        Args:
            user_query (str): User's original query
            relevant_faqs (List[Dict[str, Any]]): Relevant FAQ documents
            
        Returns:
            List[str]: List of suggested related questions
        """
        try:
            # Extract topics from relevant FAQs
            topics = set()
            for faq in relevant_faqs:
                topics.update(faq.get("tags", []))
            
            topics_str = ", ".join(list(topics)[:5])  # Limit to 5 topics
            
            system_prompt = """Based on the user's question and the related topics, suggest 3-5 related questions that might be helpful. 
Make the suggestions natural and relevant to the user's original query."""

            user_message = f"""User's Question: {user_query}
Related Topics: {topics_str}

Please suggest 3-5 related questions that might be helpful."""

            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            suggestions_text = response.choices[0].message.content
            # Parse suggestions (assuming they're numbered or bulleted)
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip() and not s.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*'))]
            
            logger.info(f"Generated {len(suggestions)} related question suggestions")
            return suggestions[:5]  # Return max 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting related questions: {str(e)}")
            return []

def create_openai_helper() -> Optional[AzureOpenAIHelper]:
    """
    Create an Azure OpenAI helper instance using environment variables.
    
    Returns:
        Optional[AzureOpenAIHelper]: Helper instance or None if configuration is missing
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
    
    if not endpoint or not key or not deployment_name:
        logger.error("Azure OpenAI configuration missing. Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, and AZURE_OPENAI_DEPLOYMENT_NAME")
        return None
    
    return AzureOpenAIHelper(endpoint, key, deployment_name, api_version)
