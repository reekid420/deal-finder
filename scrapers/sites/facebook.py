import random
import time
import requests
from bs4 import BeautifulSoup
import re
from loguru import logger
from playwright.sync_api import sync_playwright
from utils.config import USER_AGENTS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, FB_CREDENTIALS
from utils.logging_setup import SCREENSHOT_PATH

import os
import json
from pathlib import Path

class FacebookMarketplaceScraper:
    def __init__(self, headless=True):
        self.base_url = "https://www.facebook.com/marketplace/search"
        self.is_logged_in = False
        self.browser = None
        self.page = None
        self.cookies_file = "logs/fb_cookies.json"
        self.user_data_dir = os.path.abspath("logs/fb_user_data")
        self.headless = headless
        
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
            logger.info(f"Starting Facebook Marketplace search for: {keywords}")
            # Initialize and prepare browser
            products = self._search_with_browser(keywords, max_price, condition, location)
            return products
        except Exception as e:
            logger.error(f"Error searching Facebook Marketplace: {e}")
            return []
            
    def _search_with_browser(self, keywords, max_price=None, condition=None, location=None):
        """Use Playwright browser to search Facebook Marketplace"""
        products = []
        browser = None
        context = None
        
        try:
            with sync_playwright() as playwright:
                # Launch browser with more robust settings and persistent context
                logger.info("Launching browser for Facebook Marketplace")
                
                # Ensure user data directory exists
                os.makedirs(self.user_data_dir, exist_ok=True)
                
                # Use launch_persistent_context instead of passing user_data_dir as an argument
                logger.info(f"Using persistent context with user data directory: {self.user_data_dir}")
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=self.headless,  # Use the instance variable to control headless mode
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-site-isolation-trials',
                    ],
                    viewport={"width": 1280, "height": 800},
                    user_agent=random.choice(USER_AGENTS),
                    locale='en-US'
                )
                
                page = context.new_page()
                
                # Set reduced timeouts to prevent long waiting periods
                page.set_default_timeout(30000)  # 30 seconds instead of default 60
                page.set_default_navigation_timeout(30000)
                
                # Go to Facebook Marketplace directly
                logger.info("Navigating to Facebook Marketplace")
                try:
                    # First take screenshot before navigation
                    pre_nav_screenshot = os.path.join(SCREENSHOT_PATH, "fb_before_navigation.png")
                    page.screenshot(path=pre_nav_screenshot)
                    
                    # Navigate to Marketplace
                    page.goto("https://www.facebook.com/marketplace/", timeout=20000)
                    
                    # Take another screenshot after navigation
                    post_nav_screenshot = os.path.join(SCREENSHOT_PATH, "fb_after_navigation.png")
                    page.screenshot(path=post_nav_screenshot)
                    logger.info(f"Navigation screenshots saved before/after: {pre_nav_screenshot} and {post_nav_screenshot}")
                except Exception as e:
                    logger.error(f"Navigation error: {e}")
                    # Fallback to main Facebook page
                    page.goto("https://www.facebook.com/", timeout=20000)
                
                # Check login status and login if needed
                self._login_if_needed(page, context)
                
                # Try direct product search
                try:
                    # Construct search URL
                    search_url = f"https://www.facebook.com/marketplace/search?query={keywords.replace(' ', '%20')}"
                    
                    if max_price:
                        search_url += f"&maxPrice={max_price}"
                    
                    if condition:
                        condition_param = "new" if condition.lower() == "new" else "used"
                        search_url += f"&condition={condition_param}"
                    
                    logger.info(f"Navigating to search URL: {search_url}")
                    page.goto(search_url, timeout=20000)
                    
                    # Ensure user is logged in after redirect
                    self._login_if_needed(page, context)
                    
                except Exception as e:
                    logger.error(f"Search navigation error: {e}")
                    # If search URL fails, try interacting with the search box
                    try:
                        logger.info("Trying to use search box instead")
                        search_selectors = [
                            "input[placeholder*='Search Marketplace']",
                            "input[aria-label*='Search Marketplace']",
                            "input.searchbar"
                        ]
                        
                        for selector in search_selectors:
                            search_input = page.query_selector(selector)
                            if search_input:
                                logger.info(f"Found search input using selector: {selector}")
                                search_input.click()
                                search_input.fill(keywords)
                                page.keyboard.press("Enter")
                                break
                    except Exception as search_error:
                        logger.error(f"Search box interaction error: {search_error}")
                
                # Check if we're on search results page
                search_result_indicators = [
                    "h1:has-text('Search results')",
                    "[role='main'] div:has-text('Search results')",
                    "[role='main'] div:has-text('Marketplace')"
                ]
                
                search_page_identified = False
                for indicator in search_result_indicators:
                    try:
                        if page.query_selector(indicator):
                            search_page_identified = True
                            logger.info(f"Confirmed we're on search results page with indicator: {indicator}")
                            break
                    except Exception as e:
                        logger.debug(f"Error checking search page indicator {indicator}: {e}")
                
                if not search_page_identified:
                    logger.warning("Could not confirm we're on search results page")
                
                # Look for product listings with shorter timeout
                product_selectors = [
                    "a[href*='/marketplace/item/']",
                    "a[href*='/item/']",
                    "div[role='main'] a[href*='/marketplace/item/']",
                    "div[role='main'] a[href*='/item/']",
                    "div[style*='border-radius:'] a[href*='/marketplace/']"
                ]
                
                # Try to find products with each selector but don't wait too long
                product_elements = []
                found_selector = None
                
                for selector in product_selectors:
                    try:
                        # Try each selector with a short timeout
                        logger.info(f"Trying to find products with selector: {selector}")
                        elements = page.query_selector_all(selector)
                        if elements and len(elements) > 0:
                            product_elements = elements
                            found_selector = selector
                            logger.info(f"Found {len(elements)} product elements with selector: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"Error finding products with selector {selector}: {e}")
                
                # Take screenshot after product search
                products_screenshot = os.path.join(SCREENSHOT_PATH, "fb_products_found.png")
                page.screenshot(path=products_screenshot)
                logger.info(f"Saved products search screenshot to {products_screenshot}")
                
                # Check for no results message
                no_results_selectors = [
                    "text='No results found'",
                    "text='We couldn't find any results'",
                    "text='We didn't find any results'"
                ]
                
                for no_results in no_results_selectors:
                    try:
                        if page.query_selector(no_results):
                            logger.info("Facebook returned no results for this search")
                            return []  # Return empty list as there are no results
                    except Exception as e:
                        logger.debug(f"Error checking no results message: {e}")
                
                # If no product elements found via selectors, try HTML extraction
                if not product_elements:
                    logger.warning("No product elements found with selectors, trying HTML extraction")
                    try:
                        html_content = page.content()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Look for marketplace item links
                        marketplace_links = soup.find_all('a', href=lambda href: href and ('/marketplace/item/' in href or '/item/' in href))
                        
                        if marketplace_links:
                            logger.info(f"Found {len(marketplace_links)} product links in HTML")
                            
                            for link in marketplace_links:
                                try:
                                    href = link.get('href')
                                    
                                    # Extract title - look for the first reasonable text content
                                    title_candidates = []
                                    for elem in link.find_all(['span', 'div']):
                                        text = elem.get_text(strip=True)
                                        if text and len(text) > 5 and '$' not in text:
                                            title_candidates.append(text)
                                    
                                    title = title_candidates[0] if title_candidates else "Facebook Marketplace Item"
                                    
                                    # Extract price - look for text with $ sign
                                    price = 0
                                    for elem in link.find_all(['span', 'div']):
                                        text = elem.get_text(strip=True)
                                        if '$' in text:
                                            price_match = re.search(r'\$([0-9,]+(\.[0-9]{2})?)', text)
                                            if price_match:
                                                price = float(price_match.group(1).replace(',', ''))
                                                break
                                    
                                    # Create product dictionary
                                    product = {
                                        'title': title,
                                        'price': price,
                                        'link': f"https://www.facebook.com{href}" if not href.startswith('http') else href,
                                        'condition': "Not specified",
                                        'source': 'facebook'
                                    }
                                    
                                    products.append(product)
                                    logger.debug(f"Added product from HTML: {title} at ${price}")
                                except Exception as e:
                                    logger.error(f"Error processing link from HTML: {e}")
                            
                            # Return the products we found from HTML
                            if products:
                                logger.info(f"Extracted {len(products)} products from HTML")
                                if browser:
                                    browser.close()
                                    browser = None
                                return products
                    except Exception as e:
                        logger.error(f"Error with HTML extraction: {e}")
                
                # Process product elements we found from selectors
                if product_elements:
                    logger.info(f"Processing {len(product_elements)} product elements")
                    for i, element in enumerate(product_elements):
                        try:
                            # Get link
                            link = element.get_attribute('href')
                            if not link:
                                continue
                                
                            # For most Facebook items we can extract price and title from the link element
                            # or its immediate children
                            title = None
                            price = 0
                            
                            # Try to get inner text for title
                            try:
                                element_text = element.inner_text()
                                if element_text:
                                    # Split by newlines and filter
                                    lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                                    
                                    # First non-price line is probably the title
                                    for line in lines:
                                        if '$' not in line and len(line) > 5:
                                            title = line
                                            break
                                    
                                    # Look for price
                                    for line in lines:
                                        if '$' in line:
                                            price_match = re.search(r'\$([0-9,]+(\.[0-9]{2})?)', line)
                                            if price_match:
                                                price = float(price_match.group(1).replace(',', ''))
                                                break
                            except Exception as e:
                                logger.debug(f"Error extracting text from element: {e}")
                            
                            # If we couldn't get title, use a default
                            if not title:
                                title = "Facebook Marketplace Item"
                            
                            # Create product dictionary
                            product = {
                                'title': title,
                                'price': price,
                                'link': f"https://www.facebook.com{link}" if not link.startswith('http') else link,
                                'condition': "Not specified",
                                'source': 'facebook'
                            }
                            
                            products.append(product)
                            logger.debug(f"Added product: {title} at ${price}")
                            
                        except Exception as e:
                            logger.error(f"Error processing product element {i}: {e}")
                
                # Close the browser
                if browser:
                    browser.close()
                    browser = None
        
        except Exception as e:
            logger.error(f"Browser automation error: {e}")
        finally:
            # Clean up resources
            try:
                if context:
                    context.close()
                    logger.debug("Closed browser context")
            except Exception as e:
                logger.error(f"Error closing browser context: {e}")
        
        logger.info(f"Found {len(products)} products on Facebook Marketplace")
        return products
    
    def _restore_session(self, context):
        """Try to restore a previous Facebook session from cookies"""
        try:
            # Check if cookies file exists
            if os.path.exists(self.cookies_file):
                logger.info(f"Found cookies file: {self.cookies_file}")
                
                # Load cookies
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                    
                # Add cookies to context
                if cookies and len(cookies) > 0:
                    context.add_cookies(cookies)
                    logger.info(f"Restored {len(cookies)} cookies for Facebook")
                    return True
                else:
                    logger.warning("Cookies file exists but contains no cookies")
        except Exception as e:
            logger.error(f"Error restoring Facebook session from cookies: {e}")
        
        return False
        
    def _login_if_needed(self, page, context=None):
        """Attempt to log in to Facebook if credentials are available"""
        # Verify that FB_CREDENTIALS is properly loaded from environment variables
        logger.info(f"Facebook login - Email set: {bool(FB_CREDENTIALS.get('email'))}, Password set: {bool(FB_CREDENTIALS.get('password'))}")
        
        if not FB_CREDENTIALS or not FB_CREDENTIALS.get('email') or not FB_CREDENTIALS.get('password'):
            logger.warning("Facebook credentials not found, proceeding without login")
            return False
        
        # Check if we're already logged in before attempting login
        try:
            # Take screenshot of current state
            current_state_screenshot = os.path.join(SCREENSHOT_PATH, "fb_login_check.png")
            page.screenshot(path=current_state_screenshot)
            logger.info(f"Checking login state - screenshot saved to {current_state_screenshot}")
            
            # Check for login indicators in the current page
            login_indicators = [
                "[aria-label='Your profile']",
                "a[href='/marketplace/']", 
                "a[href*='/marketplace/']",
                "[role='navigation'] span:has-text('Marketplace')",
                "div[aria-label='Facebook Menu']",
                "div[role='banner'] div[aria-label='Your profile']"
            ]
            
            for indicator in login_indicators:
                try:
                    if page.query_selector(indicator):
                        logger.info(f"Already logged in to Facebook (found indicator: {indicator})")
                        return True
                except Exception as e:
                    logger.debug(f"Error checking login indicator {indicator}: {e}")
            
            # If not at the login page, go to it
            if "login" not in page.url:
                logger.info("Not on login page, navigating to it")
                page.goto("https://www.facebook.com/login", timeout=20000)
                
                # Take screenshot before login
                login_page_screenshot = os.path.join(SCREENSHOT_PATH, "fb_login_page.png")
                page.screenshot(path=login_page_screenshot)
                logger.info(f"Saved login page screenshot to {login_page_screenshot}")
            
            # Wait a moment to ensure page is loaded
            time.sleep(2)
            
            # Check for cookie consent and accept if present
            try:
                cookie_buttons = [
                    "button[data-testid='cookie-policy-manage-dialog-accept-button']",
                    "button[title='Allow all cookies']",
                    "button:has-text('Accept')",
                    "button:has-text('Accept All')",
                    "button[data-cookiebanner='accept_button']"
                ]
                
                for button_selector in cookie_buttons:
                    try:
                        cookie_button = page.query_selector(button_selector)
                        if cookie_button:
                            logger.info(f"Found cookie consent button: {button_selector}")
                            cookie_button.click()
                            time.sleep(1)
                            break
                    except Exception as e:
                        logger.debug(f"Error with cookie button {button_selector}: {e}")
            except Exception as e:
                logger.warning(f"Error handling cookie banner: {e}")
            
            # Check if login fields are visible
            email_field = page.query_selector("input#email")
            pass_field = page.query_selector("input#pass")
            login_button = page.query_selector("button[name='login']")
            
            email_visible = email_field is not None
            pass_visible = pass_field is not None
            login_button_visible = login_button is not None
            
            logger.info(f"Login form state - Email field: {email_visible}, Password field: {pass_visible}, Login button: {login_button_visible}")
            
            if not (email_visible and pass_visible and login_button_visible):
                logger.error("Login form elements not found, can't proceed with login")
                full_screenshot = os.path.join(SCREENSHOT_PATH, "fb_login_form_not_found.png")
                page.screenshot(path=full_screenshot)
                logger.info(f"Login form not found - screenshot saved to {full_screenshot}")
                return False
            
            # Fill in login form with explicit delays to ensure fields are populated
            logger.info("Entering email address")
            email_field.fill("")  # Clear first
            email_field.type(FB_CREDENTIALS['email'], delay=100)  # Slower typing like a human
            time.sleep(0.5)  # Short delay between fields
                
            logger.info("Entering password")
            pass_field.fill("")  # Clear first
            pass_field.type(FB_CREDENTIALS['password'], delay=100)  # Slower typing
            time.sleep(0.5)  # Short delay before clicking
            
            # Take screenshot after filling the form
            filled_form_screenshot = os.path.join(SCREENSHOT_PATH, "fb_filled_form.png")
            page.screenshot(path=filled_form_screenshot)
            logger.info(f"Saved filled form screenshot to {filled_form_screenshot}")
            
            # Click login button
            logger.info("Clicking login button")
            login_button.click()
            
            # Wait for navigation to complete with more robust error handling
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception as e:
                logger.warning(f"Timeout waiting for network idle after login: {e}")
                logger.info("Continuing anyway as Facebook may still be loading")
            
            # Check if login was successful with multiple verification methods
            time.sleep(2)  # Brief pause to ensure the page has loaded
            
            # Take screenshot of post-login state
            post_login_screenshot = os.path.join(SCREENSHOT_PATH, "fb_post_login.png")
            page.screenshot(path=post_login_screenshot)
            logger.info(f"Saved post-login state to {post_login_screenshot}")
            
            # Check URL and content for login success indicators
            current_url = page.url
            
            if "login" not in current_url and "checkpoint" not in current_url:
                logger.info("Successfully logged in to Facebook (URL check)")
                return True
                
            # If URL check didn't confirm login, check for elements that indicate login success
            login_success_indicators = [
                "div[role='navigation']",
                "a[href='/marketplace/']",
                "[aria-label='Your profile']",
                "div[aria-label='Facebook Menu']",
                "div[role='banner'] div[aria-label='Your profile']"
            ]
            
            for indicator in login_success_indicators:
                try:
                    if page.query_selector(indicator):
                        logger.info(f"Login confirmed via element: {indicator}")
                        return True
                except Exception as e:
                    logger.debug(f"Error checking login success indicator {indicator}: {e}")
            
            # Check for additional security checkpoints
            if "checkpoint" in current_url:
                logger.warning("Facebook security checkpoint detected. Manual intervention required.")
                checkpoint_screenshot = os.path.join(SCREENSHOT_PATH, "fb_checkpoint.png")
                page.screenshot(path=checkpoint_screenshot)
                logger.info(f"Saved checkpoint screenshot to {checkpoint_screenshot}")
                
                # Wait for user to resolve checkpoint manually
                print("\n" + "="*80)
                print("FACEBOOK SECURITY CHECKPOINT DETECTED")
                print("Please complete the security verification in the browser window")
                print("Once complete, press ENTER in this console to continue")
                print("="*80 + "\n")
                
                input("Press ENTER after completing Facebook security verification... ")
                
                # Check again if we're logged in after manual intervention
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception as e:
                    logger.warning(f"Timeout waiting for network idle after checkpoint: {e}")
                
                # Take another screenshot to see if checkpoint is resolved
                post_checkpoint_screenshot = os.path.join(SCREENSHOT_PATH, "fb_post_checkpoint.png")
                page.screenshot(path=post_checkpoint_screenshot)
                logger.info(f"Saved post-checkpoint screenshot to {post_checkpoint_screenshot}")
                
                for indicator in login_success_indicators:
                    try:
                        if page.query_selector(indicator):
                            logger.info(f"Successfully logged in after security checkpoint (found indicator: {indicator})")
                            return True
                    except Exception as e:
                        continue
                
                if "login" not in page.url and "checkpoint" not in page.url:
                    logger.info("Successfully logged in after security checkpoint verification")
                    return True
            
            logger.warning("Failed to log in to Facebook")
            failed_login_screenshot = os.path.join(SCREENSHOT_PATH, "fb_failed_login.png")
            page.screenshot(path=failed_login_screenshot)
            logger.info(f"Saved failed login screenshot to {failed_login_screenshot}")
            return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            error_screenshot = os.path.join(SCREENSHOT_PATH, "fb_login_error.png")
            try:
                page.screenshot(path=error_screenshot)
                logger.info(f"Saved login error screenshot to {error_screenshot}")
            except:
                pass
            return False
            
    def _extract_condition(self, card):
        """Extract product condition from card if available"""
        try:
            # Try multiple selectors for condition
            condition_selectors = [
                "span:has-text('New')",
                "span:has-text('Used')",
                "span:has-text('Like New')",
                "span:has-text('Good')",
                "span:has-text('Fair')",
                "span:has-text('Poor')"
            ]
            
            for selector in condition_selectors:
                condition_elem = card.query_selector(selector)
                if condition_elem:
                    condition_text = condition_elem.inner_text().strip().lower()
                    if "new" in condition_text:
                        return "New"
                    elif "like new" in condition_text:
                        return "Like New"
                    elif "good" in condition_text:
                        return "Good"
                    elif "fair" in condition_text:
                        return "Fair"
                    elif "poor" in condition_text:
                        return "Poor"
                    elif "used" in condition_text:
                        return "Used"
                        
            # If no condition found from selectors, try finding it in the text
            try:
                card_text = card.inner_text().lower()
                if "new" in card_text:
                    return "New"
                elif "like new" in card_text:
                    return "Like New"
                elif "good condition" in card_text:
                    return "Good"
                elif "fair condition" in card_text:
                    return "Fair"
                elif "poor condition" in card_text:
                    return "Poor"
                elif "used" in card_text:
                    return "Used"
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error extracting condition: {e}")
            
        return "Not specified" 