import random
import time
import requests
from bs4 import BeautifulSoup
import re
import logging
from playwright.sync_api import sync_playwright
from utils.config import USER_AGENTS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, FB_CREDENTIALS

class FacebookMarketplaceScraper:
    def __init__(self):
        self.base_url = "https://www.facebook.com/marketplace/search"
        self.is_logged_in = False
        self.browser = None
        self.page = None
        
    def search(self, keywords, max_price=None, condition=None, location=None):
        """
        Search Facebook Marketplace for products matching the keywords and filters
        
        Args:
            keywords (str): Search keywords
            max_price (float, optional): Maximum price filter
            condition (str, optional): Product condition (new, used)
            location (dict, optional): Location information for filtering
            
        Returns:
            list: List of product dictionaries
        """
        try:
            # Initialize and prepare browser
            products = self._search_with_browser(keywords, max_price, condition, location)
            return products
        except Exception as e:
            logging.error(f"Error searching Facebook Marketplace: {e}")
            return []
            
    def _search_with_browser(self, keywords, max_price=None, condition=None, location=None):
        """Use Playwright browser to search Facebook Marketplace"""
        products = []
        
        with sync_playwright() as playwright:
            try:
                # Launch browser
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={"width": 1280, "height": 720}
                )
                
                # Set random delay to avoid detection
                page.set_default_timeout(60000)  # 60 seconds timeout
                
                # Construct the search URL
                url = f"{self.base_url}/?query={'+'.join(keywords.split())}"
                
                if max_price:
                    url += f"&maxPrice={max_price}"
                
                # Add location parameter if available
                if location and 'city' in location and 'region' in location:
                    # Note: actual FB marketplace location params may vary
                    location_string = f"{location['city']}, {location['region']}"
                    url += f"&location={location_string}"
                    distance = location.get('distance', 40)  # Default to 40 miles/km
                    url += f"&distance={distance}"
                
                # Login if credentials available
                self._login_if_needed(page)
                
                # Navigate to the search URL
                logging.info(f"Searching Facebook Marketplace with URL: {url}")
                page.goto(url)
                
                # Wait for results to load
                page.wait_for_selector("div[data-testid='marketplace_search_result_content']", timeout=20000)
                
                # Scroll down to load more items (optional)
                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
                
                # Extract product information
                product_cards = page.query_selector_all("div[data-testid='marketplace_search_result_content']")
                
                for card in product_cards:
                    try:
                        # Extract product details
                        title_elem = card.query_selector("span[data-testid='marketplace_search_result_product_title']")
                        price_elem = card.query_selector("span[data-testid='marketplace_search_result_price']")
                        link_elem = card.query_selector("a[href*='/marketplace/item/']")
                        
                        if not all([title_elem, price_elem, link_elem]):
                            continue
                            
                        title = title_elem.inner_text().strip()
                        price_text = price_elem.inner_text().strip()
                        
                        # Extract numeric price with regex
                        price_match = re.search(r'\$([0-9,]+(\.[0-9]{2})?)', price_text)
                        price = float(price_match.group(1).replace(',', '')) if price_match else 0
                        
                        # Get link and extract full URL
                        link = link_elem.get_attribute("href")
                        if link and not link.startswith("http"):
                            link = f"https://www.facebook.com{link}"
                        
                        # Create product dictionary
                        product = {
                            'title': title,
                            'price': price,
                            'link': link,
                            'condition': self._extract_condition(card),
                            'source': 'facebook'
                        }
                        
                        products.append(product)
                        
                    except Exception as e:
                        logging.error(f"Error parsing product card: {e}")
                        continue
                
                # Close the browser
                browser.close()
                
            except Exception as e:
                logging.error(f"Browser automation error: {e}")
                if browser:
                    browser.close()
        
        logging.info(f"Found {len(products)} products on Facebook Marketplace")
        return products
    
    def _login_if_needed(self, page):
        """Attempt to log in to Facebook if credentials are available"""
        if not FB_CREDENTIALS or not FB_CREDENTIALS.get('email') or not FB_CREDENTIALS.get('password'):
            logging.warning("Facebook credentials not found, proceeding without login")
            return False
            
        try:
            # Go to login page
            page.goto("https://www.facebook.com/login")
            
            # Check for cookie consent and accept if present
            if page.query_selector("button[data-testid='cookie-policy-manage-dialog-accept-button']"):
                page.click("button[data-testid='cookie-policy-manage-dialog-accept-button']")
            
            # Fill in login form
            page.fill("input#email", FB_CREDENTIALS['email'])
            page.fill("input#pass", FB_CREDENTIALS['password'])
            page.click("button[name='login']")
            
            # Wait for navigation to complete
            page.wait_for_load_state("networkidle")
            
            # Check if login was successful
            if "login" not in page.url:
                logging.info("Successfully logged in to Facebook")
                return True
            else:
                logging.warning("Failed to log in to Facebook")
                return False
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            return False
    
    def _extract_condition(self, card):
        """Extract product condition from card if available"""
        try:
            condition_elem = card.query_selector("span:has-text('New') , span:has-text('Used')")
            if condition_elem:
                return condition_elem.inner_text().strip()
        except:
            pass
        return "Not specified" 