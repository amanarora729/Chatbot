import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CrawlerService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def fetch_page(self, url: str) -> str:
        try:
            logger.info(f"Fetching URL: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check for HTTP errors (4xx, 5xx)
            response.raise_for_status()
            
            # Robustness: Check Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                error_msg = f"Unsupported Content-Type: '{content_type}'. Only 'text/html' is supported."
                logger.warning(f"{error_msg} URL: {url}")
                raise ValueError(error_msg)

            logger.info(f"Successfully fetched {url}")
            return response.text
            
        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request timed out while trying to reach {url}.")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Failed to connect to {url}. The server might be unreachable or the URL is invalid.")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 404:
                raise ValueError(f"URL not found (404): {url}")
            elif status_code == 403:
                raise ValueError(f"Access forbidden (403): {url}")
            else:
                raise ConnectionError(f"HTTP error {status_code} occurred while fetching {url}")
        except requests.RequestException as e:
            raise ConnectionError(f"An error occurred while fetching {url}: {str(e)}")

    def clean_html(self, html_content: str) -> Dict[str, str]:
        if not html_content:
            return {"title": "", "text": ""}

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove irrelevant sections
        for tag in soup(['header', 'footer', 'nav', 'script', 'style', 'aside', 'iframe', 'noscript']):
            tag.decompose()

        # Remove elements with class/id names often associated with ads or irrelevant content
        irrelevant_keywords = ['ad', 'advertisement', 'social', 'popup', 'cookie', 'banner']
        for tag in soup.find_all(True):
            attr_str = str(tag.attrs).lower()
            if any(keyword in attr_str for keyword in irrelevant_keywords):
                pass 

        title = soup.title.string.strip() if soup.title else "No Title"
        
        # Get text and normalize
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.info(f"Cleaned HTML. Title: {title}, Text Length: {len(text)}")
        return {"title": title, "text": text}

    def create_chunks(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        text_len = len(text)

        if text_len == 0:
            return []

        while start < text_len:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Adjust to end at a sentence or space if possible
            if end < text_len:
                last_space = chunk_text.rfind(' ')
                if last_space != -1:
                    end = start + last_space + 1
                    chunk_text = text[start:end]

            chunks.append({
                "content": chunk_text,
                "meta_data": metadata
            })
            
            start = end - self.chunk_overlap
            if start < 0:
                start = end 
            
            if end <= start:
                start = end
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def process_url(self, url: str) -> List[Dict[str, Any]]:
        # This will now raise exceptions instead of returning empty lists on error
        html = self.fetch_page(url)
        
        if not html:
            raise ValueError("Retrieved content is empty.")
        
        cleaned_data = self.clean_html(html)
        if not cleaned_data['text']:
            logger.warning("No text content found after cleaning.")
            raise ValueError("Website content is empty or contains no extractable text after cleaning.")

        metadata = {
            "source": url,
            "title": cleaned_data['title']
        }
        
        return self.create_chunks(cleaned_data['text'], metadata)