import time
from typing import List, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from Rufus.utils.logger import get_logger
from Rufus.utils.exceptions import URLNotAccessibleError


class WebScraper:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 1)
        self.timeout = self.config.get("timeout", 60)
    
    def fetch_content(self, url: str) -> str:
        retries = 0
        while retries <= self.max_retries:
            try:
                self.logger.info(f"Fetching content from {url}")
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except RequestException as e:
                retries += 1
                if retries > self.max_retries:
                    self.logger.error(f"Failed to fetch {url} after {self.max_retries} retries: {e}")
                    raise URLNotAccessibleError(url, self.max_retries)
                wait_time = self.retry_delay * (2 ** (retries - 1))  # Exponential backoff
                self.logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    def fetch_links(self, url: str) -> List[str]:
        try:
            content = self.fetch_content(url)
            self.logger.info(f"Extracting links from {url}")
            soup = BeautifulSoup(content, 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                absolute_link = urljoin(url, a['href'])
                links.append(absolute_link)
            
            return links
        except Exception as e:
            self.logger.error(f"Error fetching links from {url}: {e}")
            return []
    
    def extract_content(self, html_content: str) -> str:
        try:
            self.logger.info("Extracting text content from HTML")
            soup = BeautifulSoup(html_content, 'html.parser') 
            for script in soup(["script", "style"]):
                script.extract()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
            
            return content
        except Exception as e:
            self.logger.error(f"Error extracting content: {e}")
            return ""
    
    def scrape_url(self, url: str) -> str:
        try:
            html_content = self.fetch_content(url)
            return self.extract_content(html_content)
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return "" 