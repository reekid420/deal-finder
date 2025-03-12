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
            url += f"&_udhi={max_price:.2f}"  # Format with 2 decimal places to match test
            
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
                    
                product = self._parse_product(listing)
                if product:
                    products.append(product)
                
            except Exception as e:
                print(f"Error parsing listing: {e}")
                continue
        
        print(f"Successfully parsed {len(products)} products")
        return products
    
    def _parse_product(self, product_element):
        """Parse a single eBay product listing element"""
        try:
            # Try multiple selectors for each element
            # Title
            title_elem = (
                product_element.select_one('.s-item__title') or 
                product_element.select_one('.item-title') or
                product_element.select_one('h3[class*="title"]')
            )
            
            # Price
            price_elem = (
                product_element.select_one('.s-item__price') or 
                product_element.select_one('.item-price') or
                product_element.select_one('span[class*="price"]')
            )
            
            # Link
            link_elem = (
                product_element.select_one('a.s-item__link') or 
                product_element.select_one('a[class*="item__link"]') or
                product_element.select_one('a[href*="itm/"]')
            )
            
            # Condition - look in multiple places
            condition_elem = (
                product_element.select_one('.SECONDARY_INFO') or 
                product_element.select_one('.s-item__subtitle') or
                product_element.select_one('span[class*="condition"]')
            )
            
            # Also check in the details section for condition
            if not condition_elem or not condition_elem.text.strip():
                detail_elems = product_element.select('.s-item__detail span')
                for elem in detail_elems:
                    text = elem.text.strip()
                    if text in ["New", "Used", "Pre-Owned", "Refurbished", "Open Box"]:
                        condition_elem = elem
                        break
            
            # Shipping
            shipping_elem = (
                product_element.select_one('.s-item__shipping') or 
                product_element.select_one('.s-item__logisticsCost') or
                product_element.select_one('span[class*="shipping"]')
            )
            
            # Image
            image_elem = (
                product_element.select_one('.s-item__image-img') or 
                product_element.select_one('img[class*="s-item"]') or
                product_element.select_one('img')
            )
            
            if not all([title_elem, price_elem, link_elem]):
                return None
                
            # Process the extracted data
            title = title_elem.text.strip()
            if title.lower() == 'shop on ebay' or not title:
                return None
                
            price = price_elem.text.strip() if price_elem else "N/A"
            url = link_elem['href'] if link_elem else None
            condition = condition_elem.text.strip() if condition_elem else "Not specified"
            shipping = shipping_elem.text.strip() if shipping_elem else "Not specified"
            image = image_elem['src'] if image_elem and 'src' in image_elem.attrs else None
            
            # Create product dictionary with the expected fields for the test
            return {
                'title': title,
                'price': price,
                'url': url,
                'condition': condition,
                'shipping': shipping,
                'image': image
            }
        except Exception as e:
            print(f"Error in _parse_product: {e}")
            return None 