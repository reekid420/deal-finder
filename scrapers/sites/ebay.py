import random
import time
import requests
from bs4 import BeautifulSoup
import re
from utils.config import USER_AGENTS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX

class EbayScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.com/sch/i.html?_nkw="
        
    def search(self, keywords, max_price=None, condition=None, location=None):
        """
        Search eBay for products matching the keywords and filters
        
        Args:
            keywords (str): Search keywords
            max_price (float, optional): Maximum price filter
            condition (str, optional): Product condition (new, used)
            location (dict, optional): Location information for filtering
            
        Returns:
            list: List of product dictionaries
        """
        # Format the search URL with parameters
        url = f"{self.base_url}{'+'.join(keywords.split())}"
        
        if max_price:
            url += f"&_udhi={max_price}"
            
        if condition:
            if condition.lower() == "new":
                url += "&LH_ItemCondition=1000"
            elif condition.lower() == "used":
                url += "&LH_ItemCondition=3000"
                
        # Add location filtering if available
        if location and 'zipcode' in location:
            distance = location.get('distance', 25)  # Default to 25 miles
            url += f"&_stpos={location['zipcode']}&_localstpos={location['zipcode']}"
            url += f"&_sadis={distance}&LH_PrefLoc=1"
        else:
            # If no location provided, use a general search
            print("No location data, using general search")
        
        # For testing purposes, try simpler URL without location parameters
        backup_url = f"{self.base_url}{'+'.join(keywords.split())}"
        if max_price:
            backup_url += f"&_udhi={max_price}"
        
        # Make the request with randomly selected user agent
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # Add delay to avoid detection
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        
        # Try with primary URL
        products = []
        try:
            print(f"Searching eBay with URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the response
            products = self._parse_search_results(response.text)
            
            # If we got products, return them
            if products:
                print(f"Found {len(products)} products with primary URL")
                return products
                
        except Exception as e:
            print(f"Error searching eBay with primary URL: {e}")
            
        # If primary search failed or returned no results, try backup URL
        if not products:
            try:
                # Use a different user agent for the backup request
                headers["User-Agent"] = random.choice(USER_AGENTS)
                
                # Add a longer delay before the backup request
                time.sleep(random.uniform(REQUEST_DELAY_MAX, REQUEST_DELAY_MAX * 2))
                
                print(f"Trying backup URL: {backup_url}")
                response = requests.get(backup_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Parse the backup response
                products = self._parse_search_results(response.text)
                print(f"Found {len(products)} products with backup URL")
                
            except Exception as e:
                print(f"Error searching eBay with backup URL: {e}")
        
        # Return products (empty list if all attempts failed)
        return products
    
    def _parse_search_results(self, html_content):
        """Parse eBay search results HTML"""
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Debug: Check if we got a captcha or blocked page
        if "robot" in html_content.lower() or "captcha" in html_content.lower():
            print("Possible CAPTCHA or anti-bot measure detected")
            # Save HTML for debugging if needed
            # with open("ebay_blocked.html", "w") as f:
            #     f.write(html_content)
            return []
            
        # Find all product listings
        # Note: eBay's HTML structure changes frequently, so try multiple selectors
        listings = soup.select('li.s-item')
        
        # If no listings found with the primary selector, try alternative selectors
        if not listings:
            print("Primary selector failed, trying alternatives")
            # Try alternative selectors that eBay might be using
            listings = soup.select('.srp-results .s-item') or soup.select('.srp-list .s-item') or soup.select('[data-view="mi:1686|iid:1"]')
        
        # Log the number of listings found
        print(f"Found {len(listings)} raw listings")
        
        for listing in listings:
            try:
                # Skip "More items like this" placeholders
                if "More items like this" in listing.text:
                    continue
                    
                # Try multiple selectors for each element
                # Title
                title_elem = (
                    listing.select_one('.s-item__title') or 
                    listing.select_one('.item-title') or
                    listing.select_one('h3[class*="title"]')
                )
                
                # Price
                price_elem = (
                    listing.select_one('.s-item__price') or 
                    listing.select_one('.item-price') or
                    listing.select_one('span[class*="price"]')
                )
                
                # Link
                link_elem = (
                    listing.select_one('a.s-item__link') or 
                    listing.select_one('a[class*="item__link"]') or
                    listing.select_one('a[href*="itm/"]')
                )
                
                # Condition
                condition_elem = (
                    listing.select_one('.SECONDARY_INFO') or 
                    listing.select_one('.s-item__subtitle') or
                    listing.select_one('span[class*="condition"]')
                )
                
                if not all([title_elem, price_elem, link_elem]):
                    continue
                    
                # Process the extracted data
                title = title_elem.text.strip()
                if title.lower() == 'shop on ebay' or not title:
                    continue
                    
                price_text = price_elem.text.strip()
                # Extract numeric price with improved regex
                price_match = re.search(r'\$([0-9,]+\.[0-9]{2})', price_text)
                if not price_match:
                    # Try alternative price format
                    price_match = re.search(r'([0-9,]+\.[0-9]{2})', price_text)
                    
                price = float(price_match.group(1).replace(',', '')) if price_match else 0
                
                link = link_elem['href']
                condition = condition_elem.text.strip() if condition_elem else "Not specified"
                
                # Create product dictionary
                product = {
                    'title': title,
                    'price': price,
                    'link': link,
                    'condition': condition,
                    'source': 'ebay'
                }
                
                products.append(product)
                
            except Exception as e:
                print(f"Error parsing listing: {e}")
                continue
        
        print(f"Successfully parsed {len(products)} products")
        return products 