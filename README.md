# 📄 Enhanced Policy Query Assistant - HackRx Bajaj Hackathon

> **AI-Powered Document Analysis System** for intelligent policy document querying with confidence scoring and multi-query processing capabilities.

## 🎯 Project Overview

This project is an **Enhanced Policy Query Assistant** built for the HackRx Bajaj Hackathon. It leverages advanced AI technologies to help users analyze policy documents (PDFs) and get intelligent answers to their questions with confidence scoring.

### 🌟 Key Features

- **📊 Confidence Scoring**: Get confidence levels for each answer
- **📋 Multiple Query Processing**: Ask several questions at once
- **📈 Document Summaries**: Generate comprehensive policy summaries
- **⚙️ Advanced Settings**: Customize processing parameters
- **🔍 Enhanced Metadata**: Detailed processing statistics
- **🛡️ Improved Error Handling**: Better error messages and validation
- **🎨 Interactive UI**: Clean, user-friendly Streamlit interface

## 🚀 Live Demo

**Streamlit Cloud**: [Policy Query Assistant](https://dynamicapppy-tcen4mzgwdphx4pacplgeh.streamlit.app/)

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: LangChain, Azure OpenAI (GPT-4o-mini, text-embedding-3-small)
- **Vector Database**: ChromaDB
- **PDF Processing**: PyPDF
- **Environment Management**: python-dotenv
- **Language**: Python 3.13+

## 📁 Project Structure

```
karam-hackrx-project/
├── 📄 dynamicapp.py          # Main Streamlit application
├── 🔧 dynamic.py             # Core document processing logic
├── 📱 karam.py               # Alternative UI implementation
├── 🗃️ app.py                 # Basic document loader
├── 📋 requirements.txt       # Python dependencies
├── 🔐 .env.example          # Environment variables template
├── 📖 DEPLOYMENT_GUIDE.md   # Deployment instructions
├── 🗂️ documents/            # Sample PDF documents
├── 💾 chroma_db/            # Vector database storage
└── 🧪 test_*.py             # Testing utilities
```

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/karamveer2648/Hackrx-Bajaj-Hackathon.git
cd Hackrx-Bajaj-Hackathon/karam-hackrx-project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your Azure OpenAI credentials
```

Add your Azure OpenAI credentials to `.env`:
```env
EMBEDDING_AZURE_API_KEY=your_embedding_api_key_here
EMBEDDING_AZURE_ENDPOINT=https://your-resource.openai.azure.com/
GENERATION_AZURE_API_KEY=your_generation_api_key_here
GENERATION_AZURE_ENDPOINT=https://your-resource.openai.azure.com/
```

### 4. Run the Application
```bash
streamlit run dynamicapp.py
```

## 🎮 How to Use

1. **Upload Document**: Upload a PDF policy document
2. **Choose Query Mode**:
   - **Single Query**: Ask one question at a time
   - **Multiple Queries**: Process several questions simultaneously
   - **Document Summary**: Get a comprehensive overview
3. **Customize Settings**: Adjust processing parameters in the sidebar
4. **Get Results**: View answers with confidence scores and source evidence

## 🔧 Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `EMBEDDING_AZURE_API_KEY` | Azure OpenAI API key for embeddings |
| `EMBEDDING_AZURE_ENDPOINT` | Azure OpenAI endpoint for embeddings |
| `GENERATION_AZURE_API_KEY` | Azure OpenAI API key for text generation |
| `GENERATION_AZURE_ENDPOINT` | Azure OpenAI endpoint for text generation |

### Advanced Settings

- **Chunk Size**: Control document splitting (500-2000)
- **Chunk Overlap**: Text overlap between chunks (50-300)
- **Max Chunks**: Maximum chunks to process (5-20)
- **Confidence Threshold**: Minimum confidence for answers (0.1-1.0)

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Fork this repository**
2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Connect your GitHub repository
   - Set main file path: `karam-hackrx-project/dynamicapp.py`

3. **Add Secrets** in Streamlit Cloud dashboard:
   ```toml
   EMBEDDING_AZURE_API_KEY = "your_api_key_here"
   EMBEDDING_AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
   GENERATION_AZURE_API_KEY = "your_api_key_here"
   GENERATION_AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
   ```

4. **Deploy and Share**!

For detailed deployment instructions, see [`DEPLOYMENT_GUIDE.md`](karam-hackrx-project/DEPLOYMENT_GUIDE.md).

## 📊 Features Deep Dive

### 🎯 Confidence Scoring
- Each answer includes a confidence percentage
- Color-coded indicators (🟢 High, 🟡 Medium, 🔴 Low)
- Warnings for low-confidence responses

### 📋 Multi-Query Processing
- Process up to 20+ questions simultaneously
- Pre-defined common policy questions
- Custom query input support
- Batch processing with individual results

### 📈 Document Analysis
- Automatic document summarization
- Metadata extraction (pages, file size, etc.)
- Source evidence tracking
- Processing statistics

## 🧪 Testing

Test the setup locally:
```bash
# Test environment variables
python test_env_vars.py

# Test SQLite compatibility (for ChromaDB)
python test_sqlite_fix.py
```

## 🛡️ Error Handling

The application includes comprehensive error handling:
- **Missing Credentials**: Clear setup instructions
- **SQLite Compatibility**: Automatic fallback for ChromaDB
- **Document Processing**: Graceful failure recovery
- **API Rate Limits**: Built-in retry mechanisms

## 🔍 Troubleshooting

### Common Issues

1. **"Missing credentials" error**:
   - Check environment variables are set
   - Verify Azure OpenAI endpoints are correct

2. **"Unsupported SQLite version" error**:
   - The app automatically handles this with `pysqlite3-binary`
   - Ensure `requirements.txt` includes all dependencies

3. **"Module not found" errors**:
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility (3.13+ recommended)

## 👥 Team

**HackRx Bajaj Hackathon Submission**
- **Developer**: Karamveer Singh
- **GitHub**: [@karamveer2648](https://github.com/karamveer2648)

## 📄 License

This project is developed for the HackRx Bajaj Hackathon. Please refer to the hackathon terms and conditions for usage rights.

## 🤝 Contributing

While this is a hackathon submission, suggestions and feedback are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
- Check the [`DEPLOYMENT_GUIDE.md`](karam-hackrx-project/DEPLOYMENT_GUIDE.md)
- Review the troubleshooting section above
- Open an issue on GitHub

---

**Made with ❤️ for HackRx Bajaj Hackathon 2025**

