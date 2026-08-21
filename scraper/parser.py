import os
import sys
import site

user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python314\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    site.addsitedir(user_site)

from urllib.parse import urljoin
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup

def extract_book_links(catalogue_html: str, catalogue_url: str) -> List[str]:
    """Extract all book detail links from a catalogue page and convert to absolute URLs."""
    soup = BeautifulSoup(catalogue_html, "html.parser")
    book_urls: List[str] = []
    
    # Find all product pods
    pods = soup.find_all("article", class_="product_pod")
    for pod in pods:
        link_tag = pod.find("h3").find("a") if pod.find("h3") else None
        if link_tag and link_tag.get("href"):
            rel_href = link_tag["href"]
            abs_url = urljoin(catalogue_url, rel_href)
            if abs_url not in book_urls:
                book_urls.append(abs_url)
                
    return book_urls

def extract_next_catalogue_url(catalogue_html: str, current_url: str) -> Optional[str]:
    """Extract next pagination catalogue URL if present."""
    soup = BeautifulSoup(catalogue_html, "html.parser")
    next_tag = soup.find("li", class_="next")
    if next_tag and next_tag.find("a") and next_tag.find("a").get("href"):
        return urljoin(current_url, next_tag.find("a")["href"])
    return None

def extract_raw_book_details(detail_html: str, product_url: str, source_page: str, fetched_at: str) -> Dict[str, Any]:
    """Extract raw field dictionary from a book detail HTML page."""
    soup = BeautifulSoup(detail_html, "html.parser")
    
    # Title
    h1 = soup.find("h1")
    title = h1.text.strip() if h1 else ""
    
    # Price
    price_tag = soup.find("p", class_="price_color")
    price_text = price_tag.text.strip() if price_tag else ""
    
    # Availability
    avail_tag = soup.find("p", class_="instock availability")
    availability_text = " ".join(avail_tag.text.split()) if avail_tag else ""
    
    # Rating text
    rating_tag = soup.find("p", class_="star-rating")
    rating_text = ""
    if rating_tag and rating_tag.get("class"):
        classes = rating_tag["class"]
        rating_text = [c for c in classes if c != "star-rating"][0] if len(classes) > 1 else ""
        
    # Description
    desc_header = soup.find("div", id="product_description")
    description = None
    if desc_header:
        p_desc = desc_header.find_next_sibling("p")
        if p_desc and p_desc.text.strip():
            description = p_desc.text.strip()
            
    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }
