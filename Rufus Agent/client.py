import asyncio
from typing import Dict, List, Optional, Any

from Rufus.models import ScrapedDocument
from Rufus.scrapers import WebScraper
from Rufus.processors import ContentProcessor
from Rufus.processors.content_processor import LinkCannotBeScrapedError
from Rufus.utils import Config, get_logger, URLNotAccessibleError


class RufusClient:
    """Client for Rufus web scraping and content processing"""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the Rufus client
        
        Args:
            api_key: API key for authentication 
            config: Configuration settings for the client (optional)
        """
        self.api_key = api_key
        self.config = Config(**(config or {}))
        self.logger = get_logger(__name__)
        self.web_scraper = WebScraper(self.config.settings)
        self.content_processor = ContentProcessor(api_key, self.config.settings)
    
    def scrape(self, url: str, instructions: str = "Extract key information") -> ScrapedDocument:
        """Scrape a URL and extract structured information based on instructions
        
        Args:
            url: URL to scrape
            instructions: Natural language instructions for content processing
            
        Returns:
            A ScrapedDocument containing the processed information
            
        Raises:
            URLNotAccessibleError: When the URL cannot be accessed after multiple retries
            LinkCannotBeScrapedError: When the link cannot be scraped due to insufficient response
            ValueError: When the website content could not be scraped or all relevant links are forbidden
        """
        try:
            self.logger.info(f"Starting to scrape {url} with instructions: {instructions}")
            return asyncio.run(self._scrape_async(url, instructions))
        except URLNotAccessibleError as e:
            self.logger.error(f"URL not accessible: {e}")
            raise
        except LinkCannotBeScrapedError as e:
            self.logger.error(f"Link cannot be scraped: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Scraping error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            raise
    
    async def _scrape_async(self, url: str, instructions: str) -> ScrapedDocument:
        """Async implementation of scrape method"""
        try:
            links = self.web_scraper.fetch_links(url)
            if not links:
                self.logger.warning(f"No links found on {url}")
            
            content = self.web_scraper.scrape_url(url)
            if not content:
                self.logger.warning(f"No content extracted from {url}")
                error_msg = f"Website could not be scraped after multiple attempts: {url}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            url_topics = await self.content_processor.assign_topics(url, links)
            if not url_topics:
                self.logger.warning("Failed to assign topics to links")
            
            relevant_urls = await self.content_processor.filter_relevant_links(
                url_topics, instructions
            )
            if not relevant_urls:
                self.logger.info("No relevant links identified")
            
            all_content = {url: content}
            forbidden_count = 0
            for rel_url in relevant_urls:
                try:
                    rel_content = self.web_scraper.scrape_url(rel_url)
                    if rel_content:
                        all_content[rel_url] = rel_content
                    else:
                        self.logger.warning(f"No content extracted from {rel_url}")
                except URLNotAccessibleError as e:
                    self.logger.error(f"Error scraping {rel_url}: {e}")
                    forbidden_count += 1
                except Exception as e:
                    self.logger.error(f"Error scraping {rel_url}: {e}")
            
            if relevant_urls and forbidden_count == len(relevant_urls):
                error_msg = "All relevant links returned forbidden URL errors"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            rag_json = await self.content_processor.generate_rag_json(
                url, instructions, all_content
            )
            
            document = ScrapedDocument.from_json(rag_json)
            self.logger.info(f"Successfully scraped {url}")
            return document
        except Exception as e:
            self.logger.error(f"Error in _scrape_async: {e}")
            raise
    
    def configure(self, **settings) -> None:
        """Update client configuration
        
        Args:
            **settings: Configuration settings to update
        """
        self.config.update(settings)
        self.web_scraper = WebScraper(self.config.settings)
        self.content_processor = ContentProcessor(self.api_key, self.config.settings) 