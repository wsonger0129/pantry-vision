"""
PantryVision Recipe Scraper

This module handles scraping real recipe data from trusted food websites.
It extracts ingredients, instructions, nutrition info, and other details from actual recipe pages.
"""

import requests
import time
import random
import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecipeScraper:
    """Scrapes real recipe data from trusted food websites."""
    
    def __init__(self):
        """Initialize the recipe scraper."""
        self.trusted_domains = {
            "allrecipes.com": self._scrape_allrecipes,
            "foodnetwork.com": self._scrape_foodnetwork,
            "bbcgoodfood.com": self._scrape_bbcgoodfood,
            "seriouseats.com": self._scrape_seriouseats,
            "bonappetit.com": self._scrape_bonappetit,
            "food.com": self._scrape_food_com,
            "tasteofhome.com": self._scrape_tasteofhome,
            "eatingwell.com": self._scrape_eatingwell,
            "cookinglight.com": self._scrape_cookinglight,
            "epicurious.com": self._scrape_epicurious
        }
        
        # User agents to rotate for requests
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1.0  # Minimum delay between requests
    
    def search_and_scrape_recipe(self, recipe_name: str, max_results: int = 3) -> List[Dict]:
        """
        Search for recipes and scrape real data from trusted sources.
        
        Args:
            recipe_name: Name of the recipe to search for
            max_results: Maximum number of recipes to return
            
        Returns:
            List of recipe dictionaries with real data
        """
        try:
            recipes = []
            
            # Try multiple search strategies
            search_strategies = [
                self._search_with_duckduckgo,
                self._search_with_direct_urls,
                self._search_with_allrecipes_direct
            ]
            
            for strategy in search_strategies:
                if len(recipes) >= max_results:
                    break
                    
                try:
                    recipe_urls = strategy(recipe_name, max_results * 2)
                    
                    for url in recipe_urls:
                        if len(recipes) >= max_results:
                            break
                            
                        # Extract domain from URL
                        domain = self._extract_domain(url)
                        if domain in self.trusted_domains:
                            try:
                                recipe_data = self._scrape_recipe_from_url(url, domain)
                                if recipe_data and self._validate_recipe_data(recipe_data):
                                    recipes.append(recipe_data)
                                    logger.info(f"Successfully scraped recipe: {recipe_data.get('name', 'Unknown')}")
                            except Exception as e:
                                logger.warning(f"Failed to scrape recipe from {url}: {e}")
                                continue
                        
                        # Rate limiting
                        self._rate_limit()
                        
                except Exception as e:
                    logger.warning(f"Search strategy failed: {e}")
                    continue
            
            return recipes
            
        except Exception as e:
            logger.error(f"Error searching and scraping recipes: {e}")
            return []
    
    def _search_with_duckduckgo(self, recipe_name: str, max_results: int) -> List[str]:
        """Search using DuckDuckGo API."""
        return self._search_recipe_urls(recipe_name, max_results)
    
    def _search_with_direct_urls(self, recipe_name: str, max_results: int) -> List[str]:
        """Search using direct URL construction for trusted sites."""
        urls = []
        # Clean the recipe name for better search results
        clean_name = self._clean_recipe_name(recipe_name)
        search_query = quote_plus(clean_name)
        
        # AllRecipes search - this will return search results page
        urls.append(f"https://www.allrecipes.com/search?q={search_query}")
        
        return urls[:max_results]
    
    def _parse_allrecipes_search_results(self, soup: BeautifulSoup) -> List[str]:
        """Parse AllRecipes search results page to find recipe URLs."""
        urls = []
        
        # Look for recipe links in search results
        recipe_links = soup.find_all('a', href=True)
        
        for link in recipe_links:
            href = link.get('href', '')
            # Check if it's a recipe URL
            if '/recipe/' in href and href not in urls:
                # Make sure it's a full URL
                if href.startswith('/'):
                    href = f"https://www.allrecipes.com{href}"
                elif href.startswith('http'):
                    pass  # Already full URL
                else:
                    continue
                
                # Validate it's a recipe page
                if '/recipe/' in href and href.endswith('/'):
                    urls.append(href)
        
        return urls[:5]  # Return top 5 results
    
    def _search_with_allrecipes_direct(self, recipe_name: str, max_results: int) -> List[str]:
        """Search AllRecipes directly for specific recipe patterns."""
        urls = []
        
        # Clean the recipe name first
        clean_name = self._clean_recipe_name(recipe_name)
        
        # Common recipe patterns for AllRecipes
        recipe_patterns = [
            clean_name.lower().replace(' ', '-'),
            clean_name.lower().replace(' ', ''),
            clean_name.lower().replace(' ', '_')
        ]
        
        for pattern in recipe_patterns:
            urls.append(f"https://www.allrecipes.com/recipe/{pattern}/")
        
        return urls[:max_results]
    
    def _clean_recipe_name(self, recipe_name: str) -> str:
        """Clean recipe name for better searching."""
        # Remove common prefixes and suffixes
        cleaned = recipe_name.strip()
        
        # Remove numbered lists (1., 2., etc.)
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
        
        # Remove common words that might interfere with search
        words_to_remove = ['recipe', 'ultimate', 'best', 'perfect', 'easy', 'quick', 'simple']
        words = cleaned.split()
        words = [word for word in words if word.lower() not in words_to_remove]
        
        return ' '.join(words)
    
    def _search_recipe_urls(self, recipe_name: str, max_results: int) -> List[str]:
        """Search for recipe URLs using DuckDuckGo."""
        try:
            # Clean the recipe name for better search results
            clean_name = self._clean_recipe_name(recipe_name)
            search_query = f"{clean_name} recipe"
            url = f"https://api.duckduckgo.com/?q={quote_plus(search_query)}&format=json&no_html=1&skip_disambig=1"
            
            headers = {
                "User-Agent": random.choice(self.user_agents)
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                urls = []
                
                # Extract URLs from response
                if data.get("AbstractURL"):
                    urls.append(data["AbstractURL"])
                
                for topic in data.get("RelatedTopics", []):
                    if isinstance(topic, dict) and topic.get("FirstURL"):
                        urls.append(topic["FirstURL"])
                
                # Filter for trusted domains
                trusted_urls = []
                for url in urls:
                    domain = self._extract_domain(url)
                    if domain in self.trusted_domains:
                        trusted_urls.append(url)
                
                return trusted_urls[:max_results]
            
        except Exception as e:
            logger.warning(f"Error searching for recipe URLs: {e}")
        
        return []
    
    def _scrape_recipe_from_url(self, url: str, domain: str) -> Optional[Dict]:
        """Scrape recipe data from a specific URL."""
        try:
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if this is a search results page
            if '/search?' in url and domain == 'allrecipes.com':
                # Parse search results to find actual recipe URLs
                recipe_urls = self._parse_allrecipes_search_results(soup)
                if recipe_urls:
                    # Try to scrape the first recipe URL found
                    first_recipe_url = recipe_urls[0]
                    logger.info(f"Found recipe URL from search: {first_recipe_url}")
                    return self._scrape_recipe_from_url(first_recipe_url, domain)
                else:
                    logger.warning(f"No recipe URLs found in search results for {url}")
                    return None
            
            # Use domain-specific scraper for actual recipe pages
            scraper_func = self.trusted_domains[domain]
            recipe_data = scraper_func(soup, url)
            
            if recipe_data:
                recipe_data['source_url'] = url
                recipe_data['scraped_from'] = domain
            
            return recipe_data
            
        except Exception as e:
            logger.warning(f"Error scraping recipe from {url}: {e}")
            return None
    
    def _scrape_allrecipes(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from AllRecipes.com."""
        try:
            # Try to find JSON-LD structured data first
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for json_ld in json_ld_scripts:
                try:
                    data = json.loads(json_ld.string)
                    # Handle both single objects and arrays
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and self._is_recipe_type(item.get('@type')):
                                return self._parse_json_ld_recipe(item)
                    elif isinstance(data, dict) and self._is_recipe_type(data.get('@type')):
                        return self._parse_json_ld_recipe(data)
                except Exception as e:
                    logger.debug(f"Error parsing JSON-LD: {e}")
                    continue
            
            # Fallback to HTML parsing
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='headline') or soup.find('h1', {'data-testid': 'recipe-title'})
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Description
            desc_elem = soup.find('div', class_='recipe-summary') or soup.find('div', {'data-testid': 'recipe-summary'})
            if desc_elem:
                recipe['description'] = desc_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('span', {'data-ingredient-name': True})
            if not ingredient_elements:
                ingredient_elements = soup.find_all('li', class_='ingredients-item')
            
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instructions-section-item')
            if not instruction_elements:
                instruction_elements = soup.find_all('div', {'data-testid': 'recipe-instruction'})
            
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            # Prep and cook time
            time_elements = soup.find_all('span', {'data-testid': 'recipe-meta-item'})
            for elem in time_elements:
                text = elem.get_text().strip()
                if 'prep' in text.lower():
                    recipe['prep_time'] = text
                elif 'cook' in text.lower():
                    recipe['cook_time'] = text
            
            # Nutrition info
            nutrition_elem = soup.find('div', {'data-testid': 'nutrition-summary'})
            if nutrition_elem:
                recipe['nutrition'] = nutrition_elem.get_text().strip()
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping AllRecipes: {e}")
            return None
    
    def _scrape_foodnetwork(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from FoodNetwork.com."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='o-AssetTitle__a-HeadlineText')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Description
            desc_elem = soup.find('div', class_='o-AssetDescription__a-Description')
            if desc_elem:
                recipe['description'] = desc_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='o-Ingredients__a-ListItem')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='o-Method__m-Step')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            # Time information
            time_elements = soup.find_all('span', class_='o-RecipeInfo__a-Description')
            for elem in time_elements:
                text = elem.get_text().strip()
                if 'prep' in text.lower():
                    recipe['prep_time'] = text
                elif 'cook' in text.lower():
                    recipe['cook_time'] = text
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping FoodNetwork: {e}")
            return None
    
    def _scrape_bbcgoodfood(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from BBC Good Food."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='post-header__title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Description
            desc_elem = soup.find('div', class_='post-header__description')
            if desc_elem:
                recipe['description'] = desc_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='pb-xxs')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='pb-xs')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping BBC Good Food: {e}")
            return None
    
    def _scrape_seriouseats(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from Serious Eats."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='recipe-title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='ingredient')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instruction')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping Serious Eats: {e}")
            return None
    
    def _scrape_bonappetit(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from Bon Appétit."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='recipe-title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='ingredient')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instruction')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping Bon Appétit: {e}")
            return None
    
    def _scrape_food_com(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from Food.com."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='recipe-title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='ingredient')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instruction')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping Food.com: {e}")
            return None
    
    def _scrape_tasteofhome(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from Taste of Home."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='recipe-title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='ingredient')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instruction')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping Taste of Home: {e}")
            return None
    
    def _scrape_eatingwell(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from EatingWell."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='recipe-title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='ingredient')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instruction')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping EatingWell: {e}")
            return None
    
    def _scrape_cookinglight(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from Cooking Light."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='recipe-title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='ingredient')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instruction')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping Cooking Light: {e}")
            return None
    
    def _scrape_epicurious(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Scrape recipe data from Epicurious."""
        try:
            recipe = {}
            
            # Recipe name
            name_elem = soup.find('h1', class_='recipe-title')
            if name_elem:
                recipe['name'] = name_elem.get_text().strip()
            
            # Ingredients
            ingredients = []
            ingredient_elements = soup.find_all('li', class_='ingredient')
            for elem in ingredient_elements:
                ingredient_text = elem.get_text().strip()
                if ingredient_text:
                    ingredients.append(ingredient_text)
            
            recipe['ingredients'] = ingredients
            
            # Instructions
            instructions = []
            instruction_elements = soup.find_all('li', class_='instruction')
            for elem in instruction_elements:
                instruction_text = elem.get_text().strip()
                if instruction_text:
                    instructions.append(instruction_text)
            
            recipe['instructions'] = instructions
            
            return recipe if recipe.get('name') else None
            
        except Exception as e:
            logger.warning(f"Error scraping Epicurious: {e}")
            return None
    
    def _parse_json_ld_recipe(self, data: Dict) -> Dict:
        """Parse JSON-LD structured data for recipes."""
        recipe = {}
        
        recipe['name'] = data.get('name', '')
        recipe['description'] = data.get('description', '')
        
        # Ingredients
        ingredients = []
        if 'recipeIngredient' in data:
            for ingredient in data['recipeIngredient']:
                if isinstance(ingredient, str):
                    ingredients.append(ingredient)
        recipe['ingredients'] = ingredients
        
        # Instructions
        instructions = []
        if 'recipeInstructions' in data:
            for instruction in data['recipeInstructions']:
                if isinstance(instruction, dict):
                    text = instruction.get('text', '')
                elif isinstance(instruction, str):
                    text = instruction
                else:
                    continue
                if text:
                    instructions.append(text)
        recipe['instructions'] = instructions
        
        # Prep time
        if 'prepTime' in data:
            recipe['prep_time'] = data['prepTime']
        
        # Cook time
        if 'cookTime' in data:
            recipe['cook_time'] = data['cookTime']
        
        # Total time
        if 'totalTime' in data:
            recipe['total_time'] = data['totalTime']
        
        # Nutrition
        if 'nutrition' in data:
            nutrition = data['nutrition']
            nutrition_parts = []
            if 'calories' in nutrition:
                nutrition_parts.append(f"Calories: {nutrition['calories']}")
            if 'proteinContent' in nutrition:
                nutrition_parts.append(f"Protein: {nutrition['proteinContent']}")
            if 'carbohydrateContent' in nutrition:
                nutrition_parts.append(f"Carbs: {nutrition['carbohydrateContent']}")
            if 'fatContent' in nutrition:
                nutrition_parts.append(f"Fat: {nutrition['fatContent']}")
            if nutrition_parts:
                recipe['nutrition'] = ", ".join(nutrition_parts)
        
        return recipe
    
    def _is_recipe_type(self, type_value) -> bool:
        """Check if the @type value indicates a recipe."""
        if isinstance(type_value, str):
            return type_value == 'Recipe'
        elif isinstance(type_value, list):
            return 'Recipe' in type_value
        return False
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    def _validate_recipe_data(self, recipe: Dict) -> bool:
        """Validate that recipe data is complete enough."""
        required_fields = ['name', 'ingredients', 'instructions']
        return all(recipe.get(field) for field in required_fields)
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        self.last_request_time = time.time()
