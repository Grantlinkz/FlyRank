import os
import sys
import site

user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python314\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    site.addsitedir(user_site)

import re
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator

class BookRecord(BaseModel):
    title: str = Field(..., description="Book title string")
    product_url: str = Field(..., description="Canonical absolute product URL")
    price_text: str = Field(..., description="Raw price text string")
    price_gbp: float = Field(..., description="Parsed price in GBP numeric float")
    availability_text: str = Field(..., description="Raw availability string")
    rating_text: str = Field(..., description="Raw star rating text")
    description: Optional[str] = Field(None, description="Book description text or None if missing")
    source_page: str = Field(..., description="Catalogue source page URL")
    fetched_at: str = Field(..., description="ISO 8601 fetch timestamp string")

    @field_validator("product_url", "source_page")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError(f"URL must start with http:// or https://, got: {v}")
        return v

def normalize_price(price_text: str) -> float:
    """Extract numeric float value from price text string (e.g. '£51.77' -> 51.77)."""
    match = re.search(r"[\d.]+", price_text)
    if match:
        return float(match.group(0))
    raise ValueError(f"Could not parse price from string: '{price_text}'")

def validate_and_normalize_records(raw_records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validate and normalize raw book records against Pydantic schema.
    Returns (valid_records, invalid_error_records).
    Identical product_urls are deduplicated (canonical URL identity).
    """
    valid_books: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    seen_urls = set()
    
    for raw in raw_records:
        product_url = raw.get("product_url", "")
        
        # Deduplication check
        if product_url in seen_urls:
            continue
            
        try:
            price_text = raw.get("price_text", "")
            price_gbp = normalize_price(price_text)
            
            payload = dict(raw)
            payload["price_gbp"] = price_gbp
            
            validated = BookRecord.model_validate(payload)
            valid_books.append(validated.model_dump())
            seen_urls.add(product_url)
        except Exception as err:
            errors.append({
                "product_url": product_url,
                "raw_record": raw,
                "error": str(err)
            })
            
    return valid_books, errors
