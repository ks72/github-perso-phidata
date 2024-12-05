"""
Scraping Agent for extracting content from ranked URLs.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
from phi.agent import Agent
from phi.llm.openai import OpenAIChat
from ..tools import FirecrawlTool


class ScrapingAgent(Agent):
    def __init__(
        self,
        name: str = "Scraping Agent",
        description: str = "Scrape text and images from ranked URLs",
        llm: Optional[OpenAIChat] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            llm=llm or OpenAIChat(model="gpt-4"),
            **kwargs,
        )
        
        # Initialize tools
        self.firecrawl_tool = FirecrawlTool()
        
        # Set the system message
        self.system_message = """You are a specialized scraping agent that extracts and processes content from ranked URLs.

Your responsibilities:
1. Extract text content and images from URLs
2. Remove duplicate content
3. Prioritize fresh content
4. Structure the content for further processing

Example output format:
{
    "scraped_content": [
        {
            "url": "example.com/article",
            "title": "2024 Market Trends",
            "text_content": [
                {
                    "type": "h1",
                    "content": "Main Heading"
                },
                {
                    "type": "p",
                    "content": "Paragraph text..."
                }
            ],
            "images": [
                {
                    "src": "example.com/image.jpg",
                    "alt": "Image description"
                }
            ]
        }
    ],
    "metadata": {
        "urls_processed": 7,
        "successful_scrapes": 6,
        "failed_scrapes": 1,
        "timestamp": "2024-01-20T10:30:00Z"
    }
}"""

    def scrape_urls(self, ranked_results: Dict, save_path: Optional[str] = None) -> Dict:
        """Scrape content from ranked URLs."""
        try:
            # Extract URLs from ranked results
            urls = [result["url"] for result in ranked_results.get("ranked_results", [])]
            
            # Use Firecrawl to scrape content
            scraped_content = self.firecrawl_tool.run(
                urls=urls,
                save_path=save_path
            )
            
            # Count successes and failures
            successful = len([r for r in scraped_content if r.get("status") == "success"])
            failed = len([r for r in scraped_content if r.get("status") == "error"])
            
            return {
                "scraped_content": scraped_content,
                "metadata": {
                    "urls_processed": len(urls),
                    "successful_scrapes": successful,
                    "failed_scrapes": failed,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "results": ranked_results
            }
    
    def process_content(self, scraped_data: Dict) -> Dict:
        """Process and structure the scraped content."""
        try:
            processed_content = []
            
            for item in scraped_data.get("scraped_content", []):
                if item.get("status") == "success":
                    # Extract main content sections
                    content = {
                        "url": item["url"],
                        "title": item["title"],
                        "main_text": self._extract_main_text(item["text_content"]),
                        "key_points": self._extract_key_points(item["text_content"]),
                        "images": self._filter_relevant_images(item["images"])
                    }
                    processed_content.append(content)
            
            return {
                "processed_content": processed_content,
                "metadata": {
                    "total_processed": len(processed_content),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "data": scraped_data
            }
    
    def _extract_main_text(self, text_content: List[Dict]) -> str:
        """Extract and combine main text content."""
        main_text = []
        for item in text_content:
            if item["type"] == "p":
                main_text.append(item["content"])
        return "\n\n".join(main_text)
    
    def _extract_key_points(self, text_content: List[Dict]) -> List[str]:
        """Extract key points from content."""
        key_points = []
        for item in text_content:
            if item["type"] in ["h1", "h2", "h3"]:
                key_points.append(item["content"])
        return key_points
    
    def _filter_relevant_images(self, images: List[Dict]) -> List[Dict]:
        """Filter and return relevant images."""
        relevant_images = []
        for image in images:
            # Skip small icons, logos, etc.
            if "icon" not in image["alt"].lower() and "logo" not in image["alt"].lower():
                relevant_images.append(image)
        return relevant_images[:5]  # Limit to top 5 relevant images
