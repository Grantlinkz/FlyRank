import os
import sys
import site

user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python314\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    site.addsitedir(user_site)

import time
import requests
from typing import Tuple

USER_AGENT = "FlyRankInternship-W5/1.0 (+https://github.com/Grantlinkz/FlyRank)"
TIMEOUT = 10
DELAY_SECONDS = 0.5

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_html(url: str, cache_name: str, force_live: bool = False) -> Tuple[str, bool, int]:
    """
    Fetch HTML content with politeness rules (user-agent, timeout, delay) and local caching.
    Returns (html_content, is_cache_hit, response_bytes).
    """
    ensure_cache_dir()
    cache_path = os.path.join(CACHE_DIR, cache_name)
    
    # Read from local disk cache if available and not forced
    if not force_live and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            content = f.read()
        size = len(content.encode("utf-8"))
        print(f"CACHE HIT: {cache_name} ({size} bytes)")
        return content, True, size
        
    # Polite delay before live network request
    time.sleep(DELAY_SECONDS)
    
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    
    if response.status_code != 200:
        raise Exception(f"HTTP fetch failed with status {response.status_code} for URL: {url}")
        
    content = response.content.decode("utf-8")
    size = len(response.content)
    
    # Save to local cache
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(content)

        
    print(f"FETCH: {url} -> {cache_name} ({size} bytes)")
    return content, False, size
