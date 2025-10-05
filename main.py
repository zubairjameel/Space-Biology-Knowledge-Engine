from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import json
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = FastAPI(title="NASA Space Biology Knowledge Engine", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for data and search
publications_df = None
vectorizer = None
tfidf_matrix = None

class PublicationSearch:
    def __init__(self):
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.abstracts_cache = {}
        self.cache_file = "abstracts_cache.json"
        
    def load_data(self, csv_path: str):
        """Load NASA publications from CSV file"""
        try:
            self.df = pd.read_csv(csv_path)
            print(f"Loaded {len(self.df)} publications")
            
            # Handle the specific CSV structure: Title, Link
            # Rename columns to standardize
            if 'Title' in self.df.columns:
                self.df = self.df.rename(columns={'Title': 'title', 'Link': 'url'})
            
            # Load cached abstracts if available
            self.load_abstracts_cache()
            
            # Create searchable text by combining title and abstract
            self.df['abstract'] = self.df['url'].apply(self.get_abstract)
            self.df['search_text'] = self.df['title'].fillna('') + ' ' + self.df['abstract'].fillna('')
            
            # Initialize TF-IDF vectorizer with more features for better search
            self.vectorizer = TfidfVectorizer(
                max_features=2000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.8
            )
            
            # Fit and transform the text data
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['search_text'].fillna(''))
            print("Enhanced TF-IDF matrix created successfully")
            
            # Save abstracts cache
            self.save_abstracts_cache()
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise e
    
    def load_abstracts_cache(self):
        """Load cached abstracts from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.abstracts_cache = json.load(f)
                print(f"Loaded {len(self.abstracts_cache)} cached abstracts")
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.abstracts_cache = {}
    
    def save_abstracts_cache(self):
        """Save abstracts cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.abstracts_cache, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(self.abstracts_cache)} abstracts to cache")
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get_abstract(self, url: str) -> str:
        """Extract abstract from PubMed Central URL"""
        if url in self.abstracts_cache:
            return self.abstracts_cache[url]
        
        try:
            # Add delay to be respectful to the server
            time.sleep(0.5)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for abstract
            abstract_selectors = [
                'div.abstract',
                'div#abstract',
                'section.abstract',
                'div.abstract-content',
                'div[data-abstract]'
            ]
            
            abstract_text = ""
            for selector in abstract_selectors:
                abstract_elem = soup.select_one(selector)
                if abstract_elem:
                    abstract_text = abstract_elem.get_text(strip=True)
                    break
            
            # If no abstract found, try to get first few paragraphs
            if not abstract_text:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    abstract_text = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
            
            # Limit abstract length
            if len(abstract_text) > 1000:
                abstract_text = abstract_text[:1000] + "..."
            
            self.abstracts_cache[url] = abstract_text
            return abstract_text
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            self.abstracts_cache[url] = ""
            return ""
    
    def search_papers(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for most relevant papers using TF-IDF"""
        if self.df is None or self.vectorizer is None:
            return []
        
        # Transform query using the same vectorizer
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include papers with some similarity
                paper = self.df.iloc[idx]
                result = {
                    "title": paper.get('title', 'No title available'),
                    "url": paper.get('url', paper.get('link', 'No URL available')),
                    "similarity_score": float(similarities[idx]),
                    "summary": self._generate_summary(paper, query)
                }
                results.append(result)
        
        return results
    
    def _generate_summary(self, paper: pd.Series, query: str) -> str:
        """Generate an intelligent summary for the paper"""
        if hasattr(self, 'openai_client') and self.openai_client:
            return self._generate_ai_summary(paper, query)
        else:
            return self._generate_rule_based_summary(paper, query)
    
    def _generate_ai_summary(self, paper: pd.Series, query: str) -> str:
        """Generate summary using advanced text analysis"""
        try:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            
            # Create a focused prompt for better summaries
            content = f"Title: {title}\nAbstract: {abstract[:800]}..."
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a NASA space biology research assistant. Provide concise, scientific summaries of research papers that help users understand key findings and their relevance to space exploration."},
                    {"role": "user", "content": f"Summarize this NASA space biology research paper in 2-3 sentences, focusing on how it relates to the question: '{query}'\n\n{content}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            return self._generate_rule_based_summary(paper, query)
    
    def _generate_rule_based_summary(self, paper: pd.Series, query: str) -> str:
        """Generate summary using rule-based analysis"""
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        
        # Extract key information from title and abstract
        query_lower = query.lower()
        title_lower = title.lower()
        
        # Find relevant keywords
        space_keywords = ['space', 'microgravity', 'radiation', 'cosmic', 'astronaut', 'mission']
        biology_keywords = ['cell', 'tissue', 'organ', 'growth', 'development', 'metabolism', 'gene']
        effect_keywords = ['effect', 'impact', 'response', 'adaptation', 'change', 'alteration']
        
        # Determine the main focus
        main_focus = []
        if any(kw in title_lower for kw in space_keywords):
            main_focus.append("space environment")
        if any(kw in title_lower for kw in biology_keywords):
            main_focus.append("biological systems")
        if any(kw in title_lower for kw in effect_keywords):
            main_focus.append("physiological effects")
        
        # Create intelligent summary based on content
        if abstract and len(abstract) > 50:
            # Extract key findings from abstract
            abstract_sentences = abstract.split('.')[:2]
            key_findings = '. '.join(abstract_sentences).strip()
            if key_findings:
                return f"Key findings: {key_findings}. This research contributes to understanding {', '.join(main_focus) if main_focus else 'space biology'}."
        
        # Fallback to title-based summary
        if main_focus:
            return f"This study examines {', '.join(main_focus)} in space conditions. The research provides valuable data for space exploration planning and biological understanding."
        else:
            return f"This NASA research investigates biological responses to space environments. The findings contribute to our understanding of life in space and future mission planning."
    
    def setup_openai(self, api_key: str):
        """Setup OpenAI client for enhanced summaries"""
        try:
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("OpenAI client initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
            self.openai_client = None

# Initialize search engine
search_engine = PublicationSearch()

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    # Try to load from different possible CSV locations
    csv_paths = [
        "SB_publication_PMC.csv",
        "nasa_publications.csv",
        "data/nasa_publications.csv", 
        "publications.csv",
        "data/publications.csv"
    ]
    
    csv_loaded = False
    for path in csv_paths:
        if os.path.exists(path):
            search_engine.load_data(path)
            csv_loaded = True
            break
    
    if not csv_loaded:
        print("No CSV file found. Please add your NASA publications CSV file.")
        print("Expected columns: title, url (or link), abstract (optional)")
    
    # Setup OpenAI if API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        search_engine.setup_openai(openai_key)
        print("OpenAI integration enabled")
    else:
        print("OpenAI not configured - using enhanced TF-IDF search")

@app.get("/")
async def root():
    return {
        "message": "NASA Space Biology Knowledge Engine API",
        "status": "running",
        "endpoints": {
            "search": "/search?query=your_question",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "publications_loaded": search_engine.df is not None,
        "total_publications": len(search_engine.df) if search_engine.df is not None else 0
    }

@app.get("/search")
async def search_publications(
    query: str = Query(..., description="Your question about space biology"),
    top_k: int = Query(3, description="Number of top results to return")
):
    """
    Search NASA space biology publications for relevant papers.
    
    Example: /search?query=How does microgravity affect plant growth?
    """
    if search_engine.df is None:
        return {
            "error": "No data loaded. Please ensure the CSV file is available.",
            "results": []
        }
    
    try:
        results = search_engine.search_papers(query, top_k)
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}",
            "results": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
