"""
PantryVision Web Search Module

Handles web search for real recipe URLs from trusted sources.
Now integrates with the recipe scraper to get actual recipe data.
"""

import requests
import time
import random
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import re
from .recipe_scraper import RecipeScraper


class RecipeWebSearch:
    """Handles web search for real recipe URLs and data."""
    
    def __init__(self):
        """Initialize the web search."""
        self.trusted_domains = [
            "allrecipes.com",
            "foodnetwork.com", 
            "bbcgoodfood.com",
            "seriouseats.com",
            "bonappetit.com",
            "food.com",
            "tasteofhome.com",
            "eatingwell.com",
            "cookinglight.com",
            "epicurious.com"
        ]
        
        # User agents to rotate for requests
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Initialize the recipe scraper
        self.recipe_scraper = RecipeScraper()
    
    def search_recipe_urls(self, recipe_name: str, max_results: int = 3) -> List[str]:
        """
        Search for real recipe URLs using DuckDuckGo instant answer API.
        
        Args:
            recipe_name: Name of the recipe to search for
            max_results: Maximum number of URLs to return
            
        Returns:
            List of real recipe URLs from trusted sources
        """
        try:
            # Create search query
            search_query = f"{recipe_name} recipe"
            
            # Use DuckDuckGo instant answer API
            url = f"https://api.duckduckgo.com/?q={quote_plus(search_query)}&format=json&no_html=1&skip_disambig=1"
            
            headers = {
                "User-Agent": random.choice(self.user_agents)
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract URLs from the response
                urls = []
                
                # Check abstract URL
                if data.get("AbstractURL"):
                    urls.append(data["AbstractURL"])
                
                # Check related topics
                for topic in data.get("RelatedTopics", []):
                    if isinstance(topic, dict) and topic.get("FirstURL"):
                        urls.append(topic["FirstURL"])
                
                # Filter for trusted domains
                trusted_urls = []
                for url in urls:
                    if any(domain in url.lower() for domain in self.trusted_domains):
                        trusted_urls.append(url)
                
                return trusted_urls[:max_results]
            
        except Exception as e:
            print(f"Web search error: {e}")
        
        # Fallback: return a generic recipe site URL
        return [f"https://www.allrecipes.com/search?q={quote_plus(recipe_name)}"]
    
    def get_recipe_source_url(self, recipe_name: str) -> str:
        """
        Get a single recipe source URL.
        
        Args:
            recipe_name: Name of the recipe
            
        Returns:
            A real recipe URL from a trusted source
        """
        urls = self.search_recipe_urls(recipe_name, max_results=1)
        
        if urls:
            return urls[0]
        else:
            # Fallback to AllRecipes search
            return f"https://www.allrecipes.com/search?q={quote_plus(recipe_name)}"
    
    def get_real_recipe_data(self, recipe_name: str, max_results: int = 3) -> List[Dict]:
        """
        Get real recipe data by scraping from trusted sources.
        
        Args:
            recipe_name: Name of the recipe to search for
            max_results: Maximum number of recipes to return
            
        Returns:
            List of recipe dictionaries with real data from trusted sources
        """
        return self.recipe_scraper.search_and_scrape_recipe(recipe_name, max_results)
    
    def get_single_real_recipe(self, recipe_name: str) -> Optional[Dict]:
        """
        Get a single real recipe with complete data.
        
        Args:
            recipe_name: Name of the recipe to search for
            
        Returns:
            Recipe dictionary with real data or None if not found
        """
        recipes = self.get_real_recipe_data(recipe_name, max_results=1)
        return recipes[0] if recipes else None
    
    def validate_url(self, url: str) -> bool:
        """
        Validate that a URL is from a trusted source.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is from trusted source, False otherwise
        """
        return any(domain in url.lower() for domain in self.trusted_domains)
