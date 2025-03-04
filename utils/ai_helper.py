import os
import json
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument, ResourceExhausted, ServiceUnavailable
import logging
from loguru import logger

# Configure the Gemini API with the API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set the model constant to use throughout
GEMINI_MODEL = "gemini-2.0-flash"
FALLBACK_MODEL = "gemini-2.0-flash-lite"

def parse_user_query(query_text, budget=None):
    """
    Parse user query for tech products using Gemini API
    
    Args:
        query_text: User's natural language query
        budget: Optional budget constraint
        
    Returns:
        dict: Structured data extracted from the query
    """
    try:
        # Build a prompt for structured data extraction
        prompt = f"""
        Parse this user query for tech products and extract structured information:
        
        Query: "{query_text}"
        Budget: ${budget if budget else 'Not specified'}
        
        Return ONLY a JSON object with these fields:
        - product_category: general category (e.g., laptop, phone, gaming)
        - product_type: specific type (e.g., gaming laptop, smartphone)
        - features: dict of important features mentioned (e.g., RAM, processor)
        - brands: array of preferred brands mentioned (e.g., ["Apple", "Samsung"])
        - budget: maximum price (use value from input, or extract from query)
        - condition: preferred condition if mentioned (new, used, refurbished, any)
        - keywords: array of important keywords for searching (combine product type with key features)
        
        DO NOT include any explanations, just the JSON object.
        
        Example:
        {{
            "product_category": "laptop",
            "product_type": "gaming laptop",
            "features": {{
                "graphics": "RTX 3060",
                "processor": "i7",
                "ram": "16GB",
                "storage": "1TB SSD"
            }},
            "brands": ["ASUS", "MSI", "Lenovo"],
            "budget": 1200,
            "condition": "new",
            "keywords": ["gaming laptop", "RTX 3060", "i7", "16GB"]
        }}
        """
        
        logger.info(f"Using Gemini model: {GEMINI_MODEL}")
        
        response_text = None
        
        # Try with the primary model first
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            generation_config = {
                "temperature": 0.1,  # Lower temperature for more deterministic outputs
                "top_p": 0.95,
                "top_k": 64,
                "response_mime_type": "application/json",  # Request explicitly as JSON
            }
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            response_text = response.text
            
        except Exception as model_error:
            logger.error(f"Error with {GEMINI_MODEL} model: {model_error}")
            
            # Try fallback model
            try:
                logger.info(f"Trying fallback model: {FALLBACK_MODEL}")
                model = genai.GenerativeModel(FALLBACK_MODEL)
                generation_config = {
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "top_k": 64,
                    "response_mime_type": "application/json",
                }
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                response_text = response.text
                
            except Exception as fallback_error:
                logger.error(f"Error with fallback model: {fallback_error}")
                # If all models fail, return basic structure from query text
                return _create_fallback_query_structure(query_text, budget)
        
        # Process and parse the response
        return _parse_ai_response(response_text, query_text, budget)
            
    except Exception as e:
        logger.error(f"Error in parse_user_query: {e}")
        return _create_fallback_query_structure(query_text, budget)

def _parse_ai_response(response_text, original_query, budget):
    """Parse the AI response and handle various JSON formats and errors"""
    if not response_text:
        return _create_fallback_query_structure(original_query, budget)
    
    # Clean up response text to extract just the JSON
    # This handles cases where the model might add explanatory text
    json_content = _extract_json_from_text(response_text)
    
    if not json_content:
        logger.warning("Could not extract JSON from response")
        return _create_fallback_query_structure(original_query, budget)
        
    try:
        # Parse the JSON content
        result = json.loads(json_content)
        
        # Verify and fix any missing fields
        result = _ensure_complete_structure(result, original_query, budget)
        result['success'] = True
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return _create_fallback_query_structure(original_query, budget)

def _extract_json_from_text(text):
    """Extract JSON content from text that might contain other elements"""
    # Look for content between curly braces
    import re
    json_pattern = r'\{[\s\S]*\}'
    matches = re.findall(json_pattern, text)
    
    if matches:
        # Get the longest match as it's likely the full JSON
        return max(matches, key=len)
    
    # If no matches with curly braces, return None
    return None

def _ensure_complete_structure(parsed_data, original_query, budget):
    """Ensure all required fields are present in the parsed data"""
    # Define default structure
    default_structure = {
        "product_category": "",
        "product_type": "",
        "features": {},
        "brands": [],
        "budget": budget if budget else 0,
        "condition": "any",
        "keywords": []
    }
    
    # Fill in any missing fields with defaults
    for key, default_value in default_structure.items():
        if key not in parsed_data or parsed_data[key] is None:
            parsed_data[key] = default_value
    
    # If keywords is empty, populate with product type and original query words
    if not parsed_data["keywords"]:
        words = [w for w in original_query.split() if len(w) > 3]
        if parsed_data["product_type"]:
            words.append(parsed_data["product_type"])
        parsed_data["keywords"] = list(set(words))
    
    return parsed_data

def _create_fallback_query_structure(query_text, budget):
    """Create a basic query structure when AI parsing fails"""
    logger.info("Using fallback query structure")
    
    # Split query into words and use words longer than 3 chars as keywords
    keywords = [word for word in query_text.split() if len(word) > 3]
    
    # Try to identify product category from common tech terms
    product_category = ""
    product_type = ""
    tech_categories = {
        "laptop": ["laptop", "notebook", "macbook", "chromebook"],
        "phone": ["phone", "smartphone", "iphone", "android"],
        "tablet": ["tablet", "ipad", "galaxy tab", "surface"],
        "desktop": ["desktop", "pc", "computer", "tower"],
        "gaming": ["gaming", "game", "xbox", "playstation", "ps5", "nintendo"],
        "audio": ["headphone", "speaker", "earbuds", "airpods", "sound"],
        "camera": ["camera", "dslr", "mirrorless", "gopro"],
        "wearable": ["watch", "smartwatch", "fitbit", "garmin", "wear"]
    }
    
    query_lower = query_text.lower()
    for category, terms in tech_categories.items():
        if any(term in query_lower for term in terms):
            product_category = category
            for term in terms:
                if term in query_lower:
                    product_type = term
                    break
            break
    
    # Extract potential condition
    condition = "any"
    if "new" in query_lower:
        condition = "new"
    elif "used" in query_lower:
        condition = "used"
    elif "refurbished" in query_lower or "refurb" in query_lower:
        condition = "refurbished"
    
    # Create and return the fallback structure
    return {
        "product_category": product_category,
        "product_type": product_type if product_type else (keywords[0] if keywords else ""),
        "features": {},
        "brands": [],
        "budget": budget if budget else 0,
        "condition": condition,
        "keywords": keywords,
        "success": False  # Indicate this is a fallback structure
    }

def rank_recommendations(products, user_preferences, budget=None):
    """
    Rank product recommendations based on user preferences
    
    Args:
        products: List of product dictionaries
        user_preferences: Structured user preferences
        budget: Optional budget constraint
        
    Returns:
        list: Ranked list of products
    """
    try:
        if len(products) <= 1:
            return products
            
        # Convert products to simplified list for AI
        product_list = []
        for i, product in enumerate(products):
            product_list.append({
                "id": i,
                "title": product["title"],
                "price": product.get("price", 0),
                "condition": product.get("condition", "unknown")
            })
            
        # Build the ranking prompt
        products_json = json.dumps(product_list)
        preferences_json = json.dumps(user_preferences)
        
        prompt = f"""
        Rank these products based on the user preferences:
        
        User preferences: {preferences_json}
        
        Products: {products_json}
        
        Return ONLY a JSON array of objects with format: 
        [
            {{"id": 0, "score": 95, "reason": "Short reason"}},
            {{"id": 2, "score": 80, "reason": "Short reason"}},
            ...
        ]
        
        Ranked from best to worst match. The "id" must match the id from the input list.
        """
        
        print(f"Using Gemini model for ranking: {GEMINI_MODEL}")
        
        # Try with primary model
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            
            # Parse the ranked result
            try:
                ranked_products = json.loads(response.text)
                
                # Reorder the original product list
                reordered_products = []
                for rank_item in ranked_products:
                    product_id = rank_item["id"]
                    if 0 <= product_id < len(products):
                        # Add the ranking reason to the product for display
                        products[product_id]["rank_reason"] = rank_item.get("reason", "")
                        products[product_id]["rank_score"] = rank_item.get("score", 0)
                        reordered_products.append(products[product_id])
                
                # If we missed any products, add them at the end
                for i, product in enumerate(products):
                    if not any(rank_item.get("id", -1) == i for rank_item in ranked_products):
                        reordered_products.append(product)
                
                return reordered_products
            except json.JSONDecodeError:
                print(f"Failed to parse ranking result: {response.text}")
                # Extract JSON array if possible
                import re
                json_pattern = r'\[.*?\]'
                matches = re.findall(json_pattern, response.text, re.DOTALL)
                if matches:
                    try:
                        # Try to parse the first JSON array-like structure
                        ranked_products = json.loads(matches[0])
                        
                        # Process as above
                        reordered_products = []
                        for rank_item in ranked_products:
                            product_id = rank_item.get("id")
                            if product_id is not None and 0 <= product_id < len(products):
                                products[product_id]["rank_reason"] = rank_item.get("reason", "")
                                products[product_id]["rank_score"] = rank_item.get("score", 0)
                                reordered_products.append(products[product_id])
                                
                        # Add missing products
                        for i, product in enumerate(products):
                            if not any(rank_item.get("id", -1) == i for rank_item in ranked_products):
                                reordered_products.append(product)
                                
                        return reordered_products
                    except:
                        pass  # Continue to fallback
                raise Exception("Invalid JSON in ranking response")
                
        except Exception as model_error:
            print(f"Error ranking with {GEMINI_MODEL}: {model_error}")
            
            # Try fallback model
            try:
                print(f"Trying fallback model for ranking: {FALLBACK_MODEL}")
                model = genai.GenerativeModel(FALLBACK_MODEL)
                response = model.generate_content(prompt)
                
                # Process response
                ranked_products = json.loads(response.text)
                
                # Reorder products
                reordered_products = []
                for rank_item in ranked_products:
                    product_id = rank_item["id"]
                    if 0 <= product_id < len(products):
                        products[product_id]["rank_reason"] = rank_item.get("reason", "")
                        products[product_id]["rank_score"] = rank_item.get("score", 0)
                        reordered_products.append(products[product_id])
                
                # Add missing products
                for i, product in enumerate(products):
                    if not any(rank_item.get("id", -1) == i for rank_item in ranked_products):
                        reordered_products.append(product)
                
                return reordered_products
            except Exception as fallback_error:
                print(f"Error with fallback ranking model: {fallback_error}")
                raise fallback_error
                
    except Exception as e:
        print(f"Error ranking products: {e}")
        # Sort by price as fallback
        sorted_products = sorted(products, key=lambda x: x.get("price", 9999))
        return sorted_products 