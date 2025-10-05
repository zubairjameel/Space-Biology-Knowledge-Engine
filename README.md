# NASA Space Biology Knowledge Engine - Backend

A comprehensive FastAPI backend that searches through NASA space biology publications and provides intelligent summaries using advanced text analysis and optional AI integration.

## 🚀 Features

- **Full-Text Search**: Searches through 608 NASA space biology publications
- **Abstract Scraping**: Automatically extracts abstracts from PubMed Central URLs
- **Intelligent Summaries**: Generates contextual summaries from actual paper content
- **Caching System**: Caches abstracts locally to avoid re-scraping
- **Dual Mode**: Works with or without OpenAI API key
- **CORS Enabled**: Ready for frontend integration

## 📁 Project Structure

```
Space-Biology-Knowledge-Engine/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── SB_publication_PMC.csv    # NASA publications dataset (608 papers)
├── abstracts_cache.json      # Cached abstracts (auto-generated)
├── env_example.txt           # Environment variables template
├── NASA_README.md            # Dataset information
└── README.md                 # This file
```

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration (Optional)
Create a `.env` file for OpenAI integration:
```bash
# Copy the template
cp env_example.txt .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Run the Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

## 🔧 Technical Architecture

### Core Components

1. **PublicationSearch Class**: Main search engine
   - Loads CSV data and creates search index
   - Scrapes abstracts from PubMed Central URLs
   - Implements TF-IDF vectorization for semantic search
   - Generates intelligent summaries

2. **Abstract Scraping**: 
   - Respectful web scraping with delays
   - Multiple selector strategies for different page layouts
   - Local caching to avoid re-scraping
   - Error handling for failed requests

3. **Search Algorithm**:
   - Enhanced TF-IDF with 2000 features
   - N-gram analysis (1-3 grams)
   - Cosine similarity for relevance scoring
   - Filters out low-similarity results

4. **Summary Generation**:
   - **With OpenAI**: AI-powered contextual summaries
   - **Without OpenAI**: Rule-based intelligent summaries
   - Keyword extraction and focus identification
   - Query-specific relevance

### API Endpoints

- `GET /` - API information and status
- `GET /health` - Health check with data loading status
- `GET /search?query=...` - Search for relevant papers

### Example API Response

```json
{
  "query": "How does microgravity affect plant growth?",
  "total_results": 3,
  "results": [
    {
      "title": "Microgravity Effects on Plant Growth and Development",
      "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/",
      "similarity_score": 0.89,
      "summary": "This study demonstrates that microgravity significantly alters plant growth patterns, showing reduced gravitropic responses and modified root development. The research provides crucial insights for space agriculture and long-duration space missions."
    }
  ]
}
```

## 🔍 Search Capabilities

The system can handle queries like:
- "How does microgravity affect plant growth?"
- "What are the effects of radiation on human cells?"
- "Space biology experiments on the International Space Station"
- "Bone loss in astronauts during spaceflight"

## 📊 Data Processing

1. **CSV Loading**: Reads NASA publications with Title and Link columns
2. **Abstract Extraction**: Scrapes abstracts from PubMed Central URLs
3. **Text Preprocessing**: Combines titles and abstracts for search
4. **Vectorization**: Creates TF-IDF matrix for semantic search
5. **Caching**: Stores abstracts locally for performance

## 🚀 Performance Features

- **Lazy Loading**: Abstracts are scraped on-demand
- **Caching**: Abstracts cached in `abstracts_cache.json`
- **Rate Limiting**: 0.5s delay between requests
- **Error Handling**: Graceful fallbacks for failed requests
- **Memory Efficient**: Processes data in chunks

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Optional OpenAI API key for enhanced summaries

### Search Parameters
- `max_features`: 2000 (TF-IDF features)
- `ngram_range`: (1, 3) for better phrase matching
- `min_df`: 2 (minimum document frequency)
- `max_df`: 0.8 (maximum document frequency)

## 🐛 Troubleshooting

### Common Issues

1. **No abstracts found**: Check internet connection and URL accessibility
2. **Slow startup**: First run scrapes abstracts, subsequent runs use cache
3. **Memory usage**: Large dataset may require 2-4GB RAM
4. **API errors**: Check OpenAI API key validity and rate limits

### Debug Mode
Add print statements in `main.py` to debug:
- Abstract scraping progress
- Search similarity scores
- Cache loading/saving

## 🎯 For Hackathon Demo

This backend provides:
1. ✅ Loads 608 NASA publications on startup
2. ✅ Scrapes abstracts from PubMed Central
3. ✅ Advanced semantic search through full text
4. ✅ Intelligent summaries from actual paper content
5. ✅ RESTful API ready for frontend integration
6. ✅ Works with or without OpenAI API key
7. ✅ Production-ready error handling and caching

## 📝 Next Steps for Frontend Integration

1. **API Integration**: Use the `/search` endpoint
2. **Error Handling**: Handle API errors gracefully
3. **Loading States**: Show progress during searches
4. **Result Display**: Format search results nicely
5. **Query Suggestions**: Add autocomplete for common queries
