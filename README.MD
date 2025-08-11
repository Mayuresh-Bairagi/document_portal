# Document Portal

![Python](https://img.shields.io/badge/PYTHON-black?style=for-the-badge&logo=python&logoColor=gold)
![HTML](https://img.shields.io/badge/HTML-black?style=for-the-badge&logo=HTML5&logoColor=E34F26)
![CSS3](https://img.shields.io/badge/CSS3-black?style=for-the-badge&logo=CSS3&logoColor=1572B6)
![Git](https://img.shields.io/badge/GIT-black?style=for-the-badge&logo=GIT&logoColor=F05032)

An intelligent document analysis and chat portal powered by LangChain, supporting multiple LLM providers and advanced document processing capabilities.

## Features

- **Document Analysis**: Advanced PDF document processing and analysis
- **Multi-Document Chat**: Interactive chat with multiple documents simultaneously  
- **Single Document Chat**: Focused conversation with individual documents
- **Document Comparison**: Compare and analyze differences between documents
- **Multiple LLM Support**: Integration with Groq and Google Gemini models
- **Vector Search**: FAISS-powered semantic search and retrieval
- **Web Interface**: Clean HTML/CSS frontend with Streamlit UI option

## Tech Stack

- **Backend**: Python, LangChain, FAISS
- **LLM Providers**: Groq (DeepSeek), Google Gemini
- **Document Processing**: PyPDF, PyMuPDF
- **Vector Database**: FAISS
- **Frontend**: HTML/CSS, Streamlit
- **Logging**: StructLog with custom logging system

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd document_portal
```

2. **Create virtual environment**
```bash
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install package in development mode**
```bash
pip install -e .
```

5. **Set up environment variables**
Create a `.env` file with your API keys:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
```

## Configuration

Edit `config/config.yml` to customize:
- LLM models and parameters
- Embedding models
- Retrieval settings
- Vector database configuration

## Usage

### Web Application
```bash
python app.py
```

### Streamlit Interface
```bash
streamlit run streamlit_ui.py
```

### Document Analysis
```python
from src.documentAnalys.analysis import DocumentAnalyzer
analyzer = DocumentAnalyzer()
results = analyzer.analyze_document("path/to/document.pdf")
```

## Project Structure

```
document_portal/
├── src/
│   ├── documentAnalys/     # Document analysis modules
│   ├── multidocChat/       # Multi-document chat functionality
│   └── singleDocChat/      # Single document chat
├── templates/              # HTML templates
├── static/                 # CSS and static files
├── config/                 # Configuration files
├── utils/                  # Utility functions
├── logger/                 # Custom logging system
├── exception/              # Custom exceptions
├── Books/                  # Sample documents
└── logs/                   # Application logs
```

## API Endpoints

- `/` - Main application interface
- Document upload and processing endpoints
- Chat and query endpoints
- Analysis and comparison endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Author

**Mayuresh Bairagi**

## Support

For issues and questions, please open an issue in the repository.