import json
import re
import asyncio
from typing import Dict, List, Any

from openai import AsyncOpenAI

from Rufus.utils.logger import get_logger


class LinkCannotBeScrapedError(Exception):
    """Raised when a link cannot be scraped due to insufficient response length."""
    pass


class ContentProcessor:
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}
        self.logger = get_logger(__name__)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = self.config.get("openai_model", "gpt-4o-mini")
    
    async def assign_topics(self, url: str, links: List[str]) -> str:
        links_text = "\n".join([f"- {link}" for link in links])
        
        topic_assignment_prompt = f"""
I've scraped the following webpage: {url}

Here are all the clickable links found on this page:
{links_text}

Based on the content of the page and the URLs themselves, assign a likely topic or category to each link.
Format your response as a list with each line containing the URL and its topic.
"""
        
        messages = [
            {
                "role": "user",
                "content": topic_assignment_prompt
            },
            {
                "role": "system",
                "content": "Analyze each URL and assign a relevant topic based on the URL structure and any context provided. Be concise but descriptive."
            }
        ]
        
        try:
            self.logger.info("Assigning topics to links")
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.config.get("max_tokens_summary", 1000),
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error assigning topics: {e}")
            return ""
    
    async def filter_relevant_links(self, url_topics: str, instructions: str) -> List[str]:
        relevance_prompt = f"""
User instructions: {instructions}

Here are the available links with their topics:
{url_topics}

Based on the user's instructions, identify which links are most relevant. 
Return ONLY the URLs that should be scraped for more information, formatted as a JSON array.
Example format: ["url1", "url2", "url3"]
"""
        
        messages = [
            {
                "role": "user",
                "content": relevance_prompt
            },
            {
                "role": "system",
                "content": "Analyze the user's instructions carefully and select only the most relevant links. Return only a JSON array of URLs."
            }
        ]
        
        try:
            self.logger.info("Filtering relevant links")
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.config.get("max_tokens_summary", 1000),
                messages=messages
            )
            
            relevant_urls_text = response.choices[0].message.content
            
            try:
                json_match = re.search(r'\[.*\]', relevant_urls_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                else:
                    return json.loads(relevant_urls_text)
            except Exception as e:
                self.logger.error(f"Error parsing relevant URLs: {e}")
                return []
        except LinkCannotBeScrapedError:
            raise
        except Exception as e:
            self.logger.error(f"Error filtering relevant links: {e}")
            return []
    
    async def generate_rag_json(self, url: str, instructions: str, content_map: Dict[str, str]) -> str:
        rag_prompt = f"""
User instructions: {instructions}

Main URL: {url}

I've scraped content from the following relevant URLs:
{json.dumps(list(content_map.keys()), indent=2)}

The content from these URLs is provided separately.

Create a comprehensive JSON object that organizes all this information in a format ready for RAG ingestion.
The JSON should include:
1. "url": The main URL being scraped
2. "summary": A summary of the main topic
3. "main_topic": The primary subject
4. "key_points": An array of key information points extracted from all sources
5. "structured_data": A structured object containing relevant data like products, features, or FAQs
6. "metadata": Information about the source
7. "sources": Array of all URLs used

IMPORTANT: Return ONLY the raw JSON without any markdown formatting, code blocks, or backticks.
Format the entire response as a single valid JSON object.
"""
        
        messages = [
            {
                "role": "user",
                "content": rag_prompt
            },
            {
                "role": "system",
                "content": "Create a well-structured, comprehensive JSON object that organizes all the information in a format suitable for RAG ingestion. Ensure the JSON is valid and properly formatted. DO NOT wrap the JSON in markdown code blocks or backticks - return ONLY the raw JSON."
            }
        ]
        
        # Add the scraped content as separate messages
        for content_url, content in content_map.items():
            content_message = f"Content from {content_url}:\n\n{content}"
            messages.append({
                "role": "user",
                "content": content_message
            })
        
        try:
            self.logger.info("Generating RAG JSON")
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.config.get("max_tokens_rag", 4000),
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error generating RAG JSON: {e}")
            return "{}" 