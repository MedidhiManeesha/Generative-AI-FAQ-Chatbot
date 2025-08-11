# 🤖 Generative AI FAQ Chatbot

A sophisticated FAQ chatbot powered by **Azure Cognitive Search** and **Azure OpenAI Service**, built with **Python** and **Streamlit**. This application provides intelligent, context-aware answers to user questions by searching through FAQ data and generating comprehensive responses using AI.

## ✨ Features

- **🔍 Semantic Search**: Uses Azure Cognitive Search with semantic capabilities to find the most relevant FAQs
- **🤖 AI-Powered Responses**: Generates intelligent answers using Azure OpenAI's GPT models
- **💬 Interactive Chat Interface**: Beautiful Streamlit-based chat UI with conversation history
- **📚 FAQ Display**: Shows top 3 relevant FAQs alongside AI-generated answers
- **💡 Smart Suggestions**: Suggests related questions based on user queries
- **📥 Conversation Export**: Download chat history as a text file
- **⚙️ Easy Configuration**: Environment-based configuration for Azure services
- **📊 Index Statistics**: Real-time monitoring of search index performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │ Azure Cognitive  │    │  Azure OpenAI   │
│                 │    │     Search       │    │     Service     │
│ • Chat Interface│◄──►│ • FAQ Indexing   │    │ • GPT Models    │
│ • User Input    │    │ • Semantic Search│    │ • Answer Gen.   │
│ • Response Display│   │ • Query Processing│   │ • Intent Analysis│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Search Engine**: Azure Cognitive Search
- **AI Service**: Azure OpenAI Service (GPT-4/GPT-35-Turbo)
- **Data Storage**: Azure Cognitive Search Index
- **Configuration**: Environment Variables

## 📋 Prerequisites

### Azure Services Setup

1. **Azure Cognitive Search Service**
   - Create an Azure Cognitive Search service in the Azure portal
   - Note down the service endpoint and admin key
   - Ensure semantic search is enabled (requires Standard tier or higher)

2. **Azure OpenAI Service**
   - Create an Azure OpenAI resource in the Azure portal
   - Deploy a GPT model (GPT-4 or GPT-35-Turbo)
   - Note down the endpoint, API key, and deployment name

### Local Development Environment

- Python 3.8 or higher
- pip package manager
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Generative-AI-FAQ-Chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and configure your Azure services:

```bash
cp env.example .env
```

Edit the `.env` file with your Azure service credentials:

```env
# Azure Cognitive Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your_search_service_admin_key
AZURE_SEARCH_INDEX_NAME=faq-index

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com
AZURE_OPENAI_KEY=your_openai_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo

# Optional: Azure OpenAI API Version
AZURE_OPENAI_API_VERSION=2023-12-01-preview
```

### 4. Prepare FAQ Data

The application includes a sample FAQ dataset in `data/faqs.csv`. You can:

- Use the provided sample data
- Replace with your own FAQ data in the same format:
  ```csv
  question,answer,tags
  "Your question here","Your answer here","tag1,tag2,tag3"
  ```

### 5. Set Up Search Index (Optional)

Run the setup script to initialize the search index:

```bash
python setup_index.py
```

This script will:
- Create the search index with semantic search capabilities
- Upload FAQ data from the CSV file
- Display index statistics

### 6. Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 📁 Project Structure

```
Generative-AI-FAQ-Chatbot/
├── app.py                 # Main Streamlit application
├── cognitive_search.py    # Azure Cognitive Search helper functions
├── openai_helper.py       # Azure OpenAI helper functions
├── setup_index.py         # Index setup script
├── requirements.txt       # Python dependencies
├── env.example           # Example environment variables
├── README.md             # Project documentation
└── data/
    └── faqs.csv          # Sample FAQ dataset
```

## 🔧 Configuration Details

### Azure Cognitive Search Index Schema

The application creates an index with the following fields:

- **id**: Unique identifier for each FAQ
- **question**: Searchable question text
- **answer**: Searchable answer content
- **tags**: Searchable and filterable tags
- **created_at**: Timestamp for document creation

### Semantic Search Configuration

The index is configured with semantic search capabilities:
- Semantic ranking for improved relevance
- Extractive captions and answers
- Language understanding for better query matching

## 🚀 Deployment

### Local Development

1. Ensure all environment variables are set
2. Run `streamlit run app.py`
3. Access the application at `http://localhost:8501`

### Azure App Service Deployment

1. **Create Azure App Service**
   ```bash
   az webapp create --name your-app-name --resource-group your-rg --plan your-plan --runtime "PYTHON|3.9"
   ```

2. **Configure Environment Variables**
   ```bash
   az webapp config appsettings set --name your-app-name --resource-group your-rg --settings \
     AZURE_SEARCH_ENDPOINT="your-endpoint" \
     AZURE_SEARCH_KEY="your-key" \
     AZURE_OPENAI_ENDPOINT="your-endpoint" \
     AZURE_OPENAI_KEY="your-key" \
     AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment"
   ```

3. **Deploy Application**
   ```bash
   az webapp deployment source config-local-git --name your-app-name --resource-group your-rg
   git remote add azure <git-url>
   git push azure main
   ```

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Run**
   ```bash
   docker build -t faq-chatbot .
   docker run -p 8501:8501 --env-file .env faq-chatbot
   ```

## 🔍 Usage

### Basic Usage

1. **Start the Application**: Run `streamlit run app.py`
2. **Ask Questions**: Type your question in the text area
3. **View Results**: See AI-generated answers and relevant FAQs
4. **Explore Suggestions**: Click on suggested related questions
5. **Download Conversations**: Use the sidebar to export chat history

### Advanced Features

- **Semantic Search**: The application uses semantic search to find the most relevant FAQs
- **Context-Aware Responses**: AI generates answers based on multiple relevant FAQs
- **Query Analysis**: The system analyzes query intent and complexity
- **Related Questions**: AI suggests follow-up questions based on the conversation

## 🛠️ Customization

### Adding Custom FAQ Data

1. Prepare your FAQ data in CSV format:
   ```csv
   question,answer,tags
   "Your question","Your answer","tag1,tag2"
   ```

2. Replace or append to `data/faqs.csv`

3. Re-run the setup script or restart the application

### Modifying AI Behavior

Edit the system prompts in `openai_helper.py`:

- **Answer Generation**: Modify the `generate_answer` method
- **Query Analysis**: Customize the `analyze_query_intent` method
- **Suggestions**: Adjust the `suggest_related_questions` method

### Customizing the UI

Modify the CSS styles in `app.py` to customize the appearance:

```python
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        /* Add your custom styles */
    }
</style>
""", unsafe_allow_html=True)
```

## 🔒 Security Considerations

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use environment variables for sensitive configuration
- **Network Security**: Ensure proper network security for Azure services
- **Access Control**: Implement appropriate access controls for production deployments

## 📊 Monitoring & Logging

The application includes comprehensive logging:

- **Search Operations**: Logs search queries and results
- **AI Interactions**: Tracks OpenAI API calls and responses
- **Error Handling**: Detailed error logging for troubleshooting
- **Performance Metrics**: Index statistics and response times

## 🐛 Troubleshooting

### Common Issues

1. **Azure Services Not Configured**
   - Verify environment variables are set correctly
   - Check Azure service endpoints and keys
   - Ensure services are running and accessible

2. **Search Index Issues**
   - Run `python setup_index.py` to recreate the index
   - Check Azure Cognitive Search service status
   - Verify semantic search is enabled

3. **OpenAI API Errors**
   - Check API key and endpoint configuration
   - Verify model deployment exists and is accessible
   - Monitor API usage and quotas

4. **Streamlit Issues**
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify port 8501 is available

### Debug Mode

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Azure Cognitive Search for powerful search capabilities
- Azure OpenAI Service for intelligent language models
- Streamlit for the beautiful web interface
- The open-source community for inspiration and tools

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review Azure service documentation

---

**Happy Chatting! 🤖💬**
