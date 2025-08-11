"""
Generative AI FAQ Chatbot - Main Application

A Streamlit-based chatbot that uses Azure Cognitive Search and Azure OpenAI
to provide intelligent answers to user questions based on FAQ data.
"""

import streamlit as st
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import our helper modules
from cognitive_search import create_search_helper
from openai_helper import create_openai_helper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Generative AI FAQ Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .faq-item {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #28a745;
    }
    .suggestion-button {
        margin: 0.25rem;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        border: 1px solid #1f77b4;
        background-color: white;
        color: #1f77b4;
        cursor: pointer;
    }
    .suggestion-button:hover {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "search_helper" not in st.session_state:
        st.session_state.search_helper = None
    if "openai_helper" not in st.session_state:
        st.session_state.openai_helper = None
    if "index_created" not in st.session_state:
        st.session_state.index_created = False

def setup_azure_services():
    """Initialize Azure services and create search index if needed."""
    try:
        # Initialize search helper
        if st.session_state.search_helper is None:
            st.session_state.search_helper = create_search_helper()
            if st.session_state.search_helper is None:
                st.error("❌ Failed to initialize Azure Cognitive Search. Please check your configuration.")
                return False
        
        # Initialize OpenAI helper
        if st.session_state.openai_helper is None:
            st.session_state.openai_helper = create_openai_helper()
            if st.session_state.openai_helper is None:
                st.error("❌ Failed to initialize Azure OpenAI. Please check your configuration.")
                return False
        
        # Create index and upload data if not already done
        if not st.session_state.index_created:
            with st.spinner("Setting up search index..."):
                if st.session_state.search_helper.create_index():
                    # Upload sample FAQ data
                    csv_path = "data/faqs.csv"
                    if os.path.exists(csv_path):
                        if st.session_state.search_helper.upload_faqs_from_csv(csv_path):
                            st.session_state.index_created = True
                            st.success("✅ Search index created and FAQ data uploaded successfully!")
                        else:
                            st.error("❌ Failed to upload FAQ data to search index.")
                            return False
                    else:
                        st.warning("⚠️ FAQ data file not found. Please ensure data/faqs.csv exists.")
                        return False
                else:
                    st.error("❌ Failed to create search index.")
                    return False
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error setting up Azure services: {str(e)}")
        return False

def display_chat_message(role: str, content: str, timestamp: str = None):
    """Display a chat message with proper styling."""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You ({timestamp}):</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 Assistant ({timestamp}):</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def display_relevant_faqs(faqs: List[Dict[str, Any]]):
    """Display relevant FAQs in an expandable section."""
    if not faqs:
        return
    
    with st.expander(f"📚 Relevant FAQs ({len(faqs)} found)", expanded=False):
        for i, faq in enumerate(faqs, 1):
            score = faq.get("score", 0)
            tags = faq.get("tags", [])
            tags_str = ", ".join(tags) if tags else "No tags"
            
            st.markdown(f"""
            <div class="faq-item">
                <h4>FAQ {i} (Relevance: {score:.3f})</h4>
                <p><strong>Q:</strong> {faq.get('question', '')}</p>
                <p><strong>A:</strong> {faq.get('answer', '')}</p>
                <p><em>Tags: {tags_str}</em></p>
            </div>
            """, unsafe_allow_html=True)

def display_suggestions(suggestions: List[str]):
    """Display suggested related questions."""
    if not suggestions:
        return
    
    st.markdown("**💡 Related questions you might want to ask:**")
    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, key=f"suggestion_{i}"):
                st.session_state.user_input = suggestion
                st.rerun()

def download_conversation():
    """Generate and provide download link for conversation history."""
    if not st.session_state.messages:
        return
    
    # Create conversation text
    conversation_text = "Generative AI FAQ Chatbot - Conversation History\n"
    conversation_text += "=" * 50 + "\n\n"
    
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        conversation_text += f"[{timestamp}] {role.upper()}: {content}\n\n"
    
    # Add metadata
    conversation_text += f"\nConversation exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Create download button
    st.download_button(
        label="📥 Download Conversation",
        data=conversation_text,
        file_name=f"faq_chatbot_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Generative AI FAQ Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("Powered by Azure Cognitive Search and Azure OpenAI")
    
    # Sidebar for configuration and controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check Azure services setup
        if setup_azure_services():
            st.success("✅ Azure services configured")
            
            # Display index statistics
            if st.session_state.search_helper:
                stats = st.session_state.search_helper.get_index_stats()
                if stats:
                    st.subheader("📊 Index Statistics")
                    st.write(f"Documents: {stats.get('document_count', 0)}")
                    st.write(f"Storage: {stats.get('storage_size', 0)} bytes")
        else:
            st.error("❌ Azure services not configured")
            st.info("Please set up your environment variables:")
            st.code("""
AZURE_SEARCH_ENDPOINT=your_search_endpoint
AZURE_SEARCH_KEY=your_search_key
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
            """)
            return
        
        # Conversation controls
        st.subheader("💬 Conversation")
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        # Download conversation
        download_conversation()
        
        # About section
        st.subheader("ℹ️ About")
        st.markdown("""
        This chatbot uses:
        - **Azure Cognitive Search** for FAQ retrieval
        - **Azure OpenAI** for intelligent responses
        - **Streamlit** for the user interface
        
        Ask any question and get AI-powered answers based on our FAQ database!
        """)
    
    # Main chat interface
    if st.session_state.messages:
        st.subheader("💬 Chat History")
        for message in st.session_state.messages:
            display_chat_message(
                message["role"],
                message["content"],
                message.get("timestamp", "")
            )
    
    # User input
    st.subheader("💭 Ask a Question")
    
    # Initialize user input in session state
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    # Text input with placeholder
    user_input = st.text_area(
        "Type your question here...",
        value=st.session_state.user_input,
        height=100,
        placeholder="e.g., How do I create an Azure OpenAI resource?"
    )
    
    # Clear the session state input after reading
    st.session_state.user_input = ""
    
    # Send button
    col1, col2 = st.columns([1, 4])
    with col1:
        send_button = st.button("🚀 Send", type="primary")
    
    # Process user input
    if send_button and user_input.strip():
        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Display user message
        display_chat_message("user", user_input, timestamp)
        
        # Process with AI
        with st.spinner("🤔 Thinking..."):
            try:
                # Search for relevant FAQs
                relevant_faqs = st.session_state.search_helper.search_faqs(user_input, top=3)
                
                # Generate AI response
                ai_response = st.session_state.openai_helper.generate_answer(user_input, relevant_faqs)
                
                # Add bot response to history
                bot_timestamp = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": bot_timestamp
                })
                
                # Display bot response
                display_chat_message("assistant", ai_response, bot_timestamp)
                
                # Display relevant FAQs
                display_relevant_faqs(relevant_faqs)
                
                # Generate and display suggestions
                suggestions = st.session_state.openai_helper.suggest_related_questions(user_input, relevant_faqs)
                if suggestions:
                    st.markdown("---")
                    display_suggestions(suggestions)
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                logger.error(f"Error processing user input: {str(e)}")
        
        # Clear the input
        st.rerun()
    
    # Welcome message for new users
    elif not st.session_state.messages:
        st.info("👋 Welcome! I'm your AI-powered FAQ assistant. Ask me anything about Azure services, and I'll provide intelligent answers based on our FAQ database.")

if __name__ == "__main__":
    main()
