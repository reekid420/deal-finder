try:
    # Basic setup
    import os
    import sys
    
    # Configure paths for imports
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Set up logging first
    from utils.logging_setup import setup_logging, SCREENSHOT_PATH, HTML_PATH
    logger = setup_logging()
    
    # Now import the rest
    import streamlit as st
    import pandas as pd
    import json
    from utils.ai_helper import parse_user_query, rank_recommendations
    from utils.location import get_user_location
    from scrapers.sites.ebay import EbayScraper
    from scrapers.sites.facebook import FacebookMarketplaceScraper
    from scrapers.sites.newegg import NeweggScraper
    from utils.config import SITES, MAX_RESULTS_PER_SITE
    from streamlit_tags import st_tags
    from streamlit_card import card
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.add_vertical_space import add_vertical_space
    import time
    
    logger.info("Successfully imported all modules for Streamlit app")
except Exception as e:
    # Log error to both console and file
    import logging
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/errors.log', 'a'),
            logging.StreamHandler()
        ]
    )
    logging.error(f"Error during import in Streamlit app: {e}", exc_info=True)
    # Re-raise to show the error in Streamlit
    raise

# Set page configuration
st.set_page_config(
    page_title="Tech Deals Finder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for improved styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8df5 !important;
        color: white !important;
    }
    .product-card {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .source-tag {
        font-size: 12px;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 10px;
        color: white;
    }
    .source-ebay {
        background-color: #e53238;
    }
    .source-facebook {
        background-color: #3b5998;
    }
    .source-newegg {
        background-color: #ff6600;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    try:
        # Main App Header
        st.markdown('<p class="main-header">🔍 Tech Deals Finder</p>', unsafe_allow_html=True)
        st.markdown("Find the best tech deals across multiple platforms with AI-powered search")
        
        # Sidebar for filters
        with st.sidebar:
            st.image("https://img.icons8.com/color/96/000000/shopping-cart--v2.png", width=80)
            st.markdown("## Search Settings")
            
            # Budget slider
            budget = st.slider("Budget ($)", min_value=0, max_value=5000, value=1000, step=100)
            
            # Site selection
            st.markdown("### Platforms to Search")
            ebay_enabled = st.checkbox("eBay", value=SITES["ebay"]["enabled"])
            facebook_enabled = st.checkbox("Facebook Marketplace", value=SITES["facebook"]["enabled"])
            newegg_enabled = st.checkbox("Newegg", value=SITES["newegg"]["enabled"])
            
            # Condition filter
            condition = st.radio(
                "Product Condition",
                options=["Any", "New", "Used", "Refurbished"],
                horizontal=True,
                index=0
            )
            
            # Location settings
            st.markdown("### Location Settings")
            
            # Get user location if not already in session state
            if 'location' not in st.session_state:
                with st.spinner("Detecting your location..."):
                    st.session_state.location = get_user_location()
            
            location = st.session_state.location
            
            # Add manual location override option
            use_manual_location = st.checkbox("Specify my location manually", 
                                                  help="Use this if your location was detected incorrectly")
            
            if use_manual_location:
                from utils.location import get_location_by_address
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    location_input = st.text_input(
                        "Enter your location",
                        placeholder="e.g., Warrenton, NC or Warren County, NC"
                    )
                
                with col2:
                    lookup_button = st.button("Set Location", use_container_width=True)
                
                if location_input and lookup_button:
                    with st.spinner("Looking up location..."):
                        manual_location = get_location_by_address(location_input)
                        if manual_location:
                            st.session_state.location = manual_location
                            location = manual_location
                            st.success(f"📍 Set to: {manual_location.get('city', '')}, " + 
                                      f"{manual_location.get('region', '')}" + 
                                      (f" ({manual_location.get('county', '')})" if manual_location.get('county') else ""))
                        else:
                            st.error("Location not found. Please try a different location format.")
            
            if location:
                if not use_manual_location:
                    st.info(f"📍 Auto-detected: {location.get('city')}, {location.get('region')}")
                search_radius = st.slider("Search Radius (miles)", 5, 100, 25)
                location['distance'] = search_radius
            else:
                st.warning("Location detection failed. Using general search.")
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Query input section
            colored_header(label="What are you looking for?", description="Describe the tech product you want to find", color_name="blue-70")
            
            query = st.text_area(
                "Describe what you want to find in detail",
                placeholder="e.g., 'gaming laptop with RTX graphics card under $1200' or 'used iPhone 13 in good condition'",
                height=100
            )
            
            # Additional tags for keywords
            additional_keywords = st_tags(
                label="Add specific keywords (optional)",
                text="Press enter to add more",
                value=[],
                suggestions=["gaming", "laptop", "phone", "tablet", "headphones", "camera"],
                maxtags=5
            )
        
        with col2:
            # Search button and advanced options
            add_vertical_space(2)
            
            st.info("💡 **Tip**: Be specific about features, brands, and condition to get better results.")
            
            # Advanced options expander
            with st.expander("Advanced Options"):
                sort_by = st.radio("Sort Results By", ["AI Recommendation", "Price (Low to High)", "Price (High to Low)"], index=0)
                max_results = st.slider("Maximum Results per Site", 10, MAX_RESULTS_PER_SITE, 20)
            
            # Search button
            search_col1, search_col2 = st.columns([3, 1])
            with search_col1:
                search_button = st.button("🔍 Search Deals", type="primary", use_container_width=True)
            with search_col2:
                clear_button = st.button("Clear", type="secondary", use_container_width=True)
                if clear_button:
                    # Clear results if they exist
                    if 'search_results' in st.session_state:
                        del st.session_state.search_results
                    st.experimental_rerun()
        
        # Process search when button is clicked
        if search_button:
            if not query:
                st.error("Please enter a search query")
                return
            
            # Store selected platforms
            active_platforms = []
            if ebay_enabled:
                active_platforms.append("ebay")
            if facebook_enabled:
                active_platforms.append("facebook")
            if newegg_enabled:
                active_platforms.append("newegg")
            
            if not active_platforms:
                st.error("Please select at least one platform to search")
                return
            
            # Create search progress tracker
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Combine query with additional keywords
            full_query = query
            if additional_keywords:
                full_query += " " + " ".join(additional_keywords)
            
            with st.spinner("Processing your request..."):
                # Step 1: Parse the query using AI
                status_text.text("Analyzing your request with AI...")
                progress_bar.progress(10)
                
                parsed_query = parse_user_query(full_query, budget)
                progress_bar.progress(30)
                
                # Create expandable debug section
                with st.expander("Query Analysis Details"):
                    st.json(parsed_query)
                
                # Extract search parameters from parsed query
                try:
                    # Extract keywords for search
                    if parsed_query.get('keywords'):
                        search_keywords = " ".join(parsed_query.get('keywords'))
                    else:
                        # Fallback to raw query
                        search_keywords = full_query
                    
                    # Extract max price and condition
                    max_price = parsed_query.get('budget', budget)
                    search_condition = parsed_query.get('condition', '').lower()
                    
                    # Default to selected condition if not detected in query
                    if not search_condition or search_condition == 'any':
                        search_condition = condition.lower() if condition.lower() != 'any' else None
                    
                    # Start collecting results from selected platforms
                    all_results = []
                    
                    # Step 2: Search eBay if enabled
                    if "ebay" in active_platforms:
                        status_text.text("Searching eBay...")
                        progress_bar.progress(40)
                        
                        ebay_scraper = EbayScraper()
                        ebay_results = ebay_scraper.search(
                            search_keywords, 
                            max_price=max_price, 
                            condition=search_condition,
                            location=location
                        )
                        
                        logger.info(f"Found {len(ebay_results)} results from eBay")
                        all_results.extend(ebay_results)
                        progress_bar.progress(60)
                    
                    # Step 3: Search Facebook if enabled
                    if "facebook" in active_platforms:
                        status_text.text("Searching Facebook Marketplace...")
                        progress_bar.progress(70)
                        
                        facebook_scraper = FacebookMarketplaceScraper()
                        facebook_results = facebook_scraper.search(
                            search_keywords, 
                            max_price=max_price, 
                            condition=search_condition,
                            location=location
                        )
                        
                        logger.info(f"Found {len(facebook_results)} results from Facebook")
                        all_results.extend(facebook_results)
                        progress_bar.progress(85)
                    
                    # Step 4: Search Newegg if enabled
                    if "newegg" in active_platforms:
                        status_text.text("Searching Newegg...")
                        progress_bar.progress(85)
                        
                        newegg_scraper = NeweggScraper()
                        newegg_results = newegg_scraper.search(
                            search_keywords, 
                            max_price=max_price, 
                            condition=search_condition,
                            location=location
                        )
                        
                        logger.info(f"Found {len(newegg_results)} results from Newegg")
                        all_results.extend(newegg_results)
                        progress_bar.progress(90)
                    
                    # Step 5: Rank results if we have enough products
                    if len(all_results) > 3:
                        status_text.text("Ranking recommendations for you...")
                        
                        # Apply sorting based on user selection
                        if sort_by == "AI Recommendation" and len(all_results) > 3:
                            progress_bar.progress(95)
                            all_results = rank_recommendations(all_results, parsed_query)
                        elif sort_by == "Price (Low to High)":
                            all_results.sort(key=lambda x: x.get('price', 9999))
                        elif sort_by == "Price (High to Low)":
                            all_results.sort(key=lambda x: x.get('price', 0), reverse=True)
                    
                    # Cap the results per user selection
                    all_results = all_results[:max_results*len(active_platforms)]
                    
                    # Store results in session state
                    st.session_state.search_results = all_results
                    
                    # Complete the progress
                    progress_bar.progress(100)
                    status_text.text("Search complete!")
                    time.sleep(0.5)  # Brief pause to show completion
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Display results
                    display_search_results(all_results, parsed_query)
                    
                except Exception as e:
                    st.error(f"Error processing search results: {str(e)}")
                    logger.error(f"Search error: {e}")
                    st.write("Please try a more specific search query.")
            
        # Display previous results if they exist
        elif 'search_results' in st.session_state:
            display_search_results(st.session_state.search_results, {})
    except Exception as e:
        logger.error(f"Error in Streamlit app: {e}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check the logs for more details.")


def display_search_results(results, parsed_query):
    """Display search results with improved UI"""
    if not results:
        st.warning("🔍 No results found. Try different search terms or relaxing your filters.")
        return
    
    # Show success message with result count
    st.success(f"✅ Found {len(results)} results")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Card View", "Table View"])
    
    with tab1:
        # Card view
        st.markdown("### Top Recommendations")
        
        # Create cards in rows of 3
        for i in range(0, len(results), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(results):
                    product = results[i+j]
                    with cols[j]:
                        # Determine source for styling
                        source_class = f"source-{product.get('source', 'other')}"
                        
                        # Create card
                        with st.container():
                            st.markdown(f"""
                            <div class="product-card">
                                <span class="source-tag {source_class}">{product.get('source', '').upper()}</span>
                                <h3>{product.get('title', 'Product')}</h3>
                                <h2 style="color: #4CAF50;">${product.get('price', 0):.2f}</h2>
                                <p><strong>Condition:</strong> {product.get('condition', 'Not specified')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'link' in product:
                                st.markdown(f"[View Details]({product['link']})")
    
    with tab2:
        # Table view
        # Convert to DataFrame for display
        df = pd.DataFrame(results)
        
        # Format the DataFrame
        if 'price' in df.columns:
            df['price'] = df['price'].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")
        
        display_columns = [col for col in ['title', 'price', 'condition', 'source'] if col in df.columns]
        st.dataframe(df[display_columns], use_container_width=True)
    
    # Additional information about the search
    with st.expander("Search Details"):
        if parsed_query:
            st.write("**Product Category:**", parsed_query.get('product_category', 'Not specified'))
            st.write("**Product Type:**", parsed_query.get('product_type', 'Not specified'))
            
            # Show features if available
            features = parsed_query.get('features', {})
            if features:
                st.write("**Detected Features:**")
                for feature, value in features.items():
                    st.write(f"- {feature.title()}: {value}")
            
            # Show brands if available
            brands = parsed_query.get('brands', [])
            if brands:
                st.write("**Preferred Brands:**", ", ".join(brands))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception in Streamlit app: {e}", exc_info=True)
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error("Please check the logs for more details.") 