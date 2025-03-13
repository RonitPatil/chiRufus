## How Rufus Works

Rufus follows a multi-tier architecture to scrape and process web content:

### 1. Preprocessing Tier
- Extracts all clickable links from the target webpage using BeautifulSoup4
- Handles URL normalization and validation

### 2. Scraping Tier
- Scrapes the main webpage and extracts content
- Processes HTML to clean and structure the text
- Adds contextual information to the extracted links

### 3. Filtering Tier
- Uses LLM to analyze and categorize extracted links
- Filters links based on relevance to user instructions
- Implements intelligent content selection

### 4. Generation Tier
- Processes all relevant content using OpenAI's API
- Generates structured JSON output
- Ensures consistent document format through the ScrapedDocument class

## Installation

```bash
pip install -e .
```

## Integrating with RAG Pipeline

Rufus is designed to seamlessly integrate with Retrieval-Augmented Generation (RAG) pipelines. Here's how to incorporate it:

### 1. Document Generation
```python
from Rufus import RufusClient

client = RufusClient(api_key=your_api_key)

document = client.scrape(
    url="https://your-target-url.com",
    instructions="Extract specific information about..."
)
```

### 2. RAG Integration Options

#### A. Direct Vector Store Integration
```python
import chromadb

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="your_collection")

documents = [
    {
        "text": document.summary + "\n" + "\n".join(document.key_points),
        "metadata": {
            "url": document.url,
            "main_topic": document.main_topic,
            **document.metadata
        }
    }
]

collection.add(
    documents=documents,
    metadatas=[doc["metadata"] for doc in documents],
    ids=[f"doc_{i}" for i in range(len(documents))]
)
```

#### B. LangChain Integration
```python
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

langchain_docs = [
    Document(
        page_content=document.summary + "\n" + "\n".join(document.key_points),
        metadata={
            "url": document.url,
            "main_topic": document.main_topic,
            "source": "rufus_scraper",
            **document.metadata
        }
    )
]

vectorstore = Chroma.from_documents(
    documents=langchain_docs,
    embedding=OpenAIEmbeddings()
)
```

### Key Features
- Asynchronous processing for improved performance
- Robust error handling and logging
- Configurable settings for customization
- Support for nested page traversal (up to depth 2)
- Standardized JSON output format

## Advanced Configuration

You can customize the client behavior with configuration settings:

```python
client = RufusClient(
    api_key=api_key, 
    config={
        "openai_model": "gpt-4o-mini",
        "max_retries": 3,
        "retry_delay": 1,
        "timeout": 60,
        "max_tokens_summary": 1000,
        "max_tokens_rag": 4000,
    }
)

client.configure(
    max_retries=5,
    timeout=120
)
```

### Best Practices for RAG Integration

1. **Content Processing**
   - Use the `summary` and `key_points` for concise context
   - Leverage `structured_data` for domain-specific information
   - Include `sources` for reference and attribution

2. **Metadata Handling**
   - Utilize `metadata` for filtering and retrieval
   - Include `main_topic` for content categorization
   - Store `url` for source tracking

3. **Performance Optimization**
   - Configure `max_tokens_summary` and `max_tokens_rag` based on your needs
   - Use async processing for batch operations
   - Implement proper error handling and retries

4. **Quality Control**
   - Validate scraped content before ingestion
   - Monitor and log processing steps
   - Implement content deduplication if needed