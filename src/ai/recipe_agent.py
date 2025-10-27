"""
PantryVision AI Recipe Agent

This module provides an AI agent that recommends recipes based on user preferences,
fitness goals, and dietary restrictions using OpenAI's API.
"""

import os
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import data storage, models, and utilities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from data.storage import DataStorage
from models import UserProfile
from utils.web_search import RecipeWebSearch
from utils.preference_matcher import SmartPreferenceMatcher


class RecipeAgent:
    """AI agent for recipe recommendations using OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, 
                 max_tokens: Optional[int] = None, temperature: Optional[float] = None,
                 save_data: Optional[bool] = None, data_dir: Optional[str] = None):
        """
        Initialize the Recipe Agent.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: OpenAI model to use. If None, will get from environment.
            max_tokens: Maximum tokens for responses. If None, will get from environment.
            temperature: Temperature for responses. If None, will get from environment.
            save_data: Whether to save user data locally. If None, will get from environment.
            data_dir: Directory for data storage. If None, will get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Model configuration
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = max_tokens or int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.temperature = temperature or float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        # Data persistence configuration
        self.save_data = save_data if save_data is not None else os.getenv("SAVE_USER_DATA", "true").lower() == "true"
        self.data_dir = data_dir or os.getenv("DATA_DIR", "./data")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Initialize data storage
        self.storage = DataStorage(self.data_dir) if self.save_data else None
        
        # Initialize web search and preference matching
        self.web_search = RecipeWebSearch()
        self.preference_matcher = SmartPreferenceMatcher()
        
        # Load existing user profile if available
        self.user_profile: Optional[UserProfile] = None
        if self.save_data and self.storage:
            self.user_profile = self.storage.load_user_profile()
            if self.user_profile:
                print("Loaded existing user profile from local storage.")
        
    def collect_user_profile(self) -> UserProfile:
        """
        Collect user preferences, fitness goals, and allergies through interactive prompts.
        
        Returns:
            UserProfile object with user's information
        """
        print("\nWelcome to PantryVision! Let's personalize your recipe recommendations.")
        print("=" * 60)
        
        # Collect preferences
        print("\nWhat are your food preferences? (e.g., 'love meat', 'vegetarian', 'love spicy food')")
        print("Enter multiple preferences separated by commas:")
        preferences_input = input("Preferences: ").strip()
        preferences = [p.strip() for p in preferences_input.split(",") if p.strip()]
        
        # Collect fitness goals
        print("\nWhat are your fitness goals? (e.g., 'high protein', 'low calorie', 'bulking', 'cutting', 'muscle building')")
        print("Enter multiple goals separated by commas:")
        goals_input = input("Fitness goals: ").strip()
        fitness_goals = [g.strip() for g in goals_input.split(",") if g.strip()]
        
        # Collect allergies
        print("\nDo you have any allergies? (e.g., 'nuts', 'dairy', 'gluten', 'shellfish')")
        print("Enter 'none' if no allergies, or list them separated by commas:")
        allergies_input = input("Allergies: ").strip().lower()
        allergies = [] if allergies_input == "none" else [a.strip() for a in allergies_input.split(",") if a.strip()]
        
        # Collect dietary restrictions
        print("\nAny dietary restrictions or preferences? (e.g., 'keto', 'paleo', 'mediterranean', 'low carb')")
        print("Enter 'none' if no restrictions, or list them separated by commas:")
        restrictions_input = input("Dietary restrictions: ").strip().lower()
        dietary_restrictions = [] if restrictions_input == "none" else [r.strip() for r in restrictions_input.split(",") if r.strip()]
        
        self.user_profile = UserProfile(
            preferences=preferences,
            fitness_goals=fitness_goals,
            allergies=allergies,
            dietary_restrictions=dietary_restrictions
        )
        
        # Save profile to local storage if enabled
        if self.save_data and self.storage:
            if self.storage.save_user_profile(self.user_profile):
                print("Profile saved to local storage!")
            else:
                print("Warning: Failed to save profile to local storage.")
        
        print(f"\nProfile saved! Here's what I'll consider:")
        print(f"   Preferences: {', '.join(preferences) if preferences else 'None specified'}")
        print(f"   Fitness goals: {', '.join(fitness_goals) if fitness_goals else 'None specified'}")
        print(f"   Allergies: {', '.join(allergies) if allergies else 'None'}")
        print(f"   Dietary restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}")
        
        return self.user_profile
    
    def get_recipe_recommendations(self, user_request: str, num_recipes: int = 3) -> List[Dict]:
        """
        Get recipe recommendations based on user request and profile.
        Now generates complete recipes directly from AI without web scraping.
        
        Args:
            user_request: User's request (e.g., "I want meat for dinner tonight")
            num_recipes: Number of recipes to recommend
            
        Returns:
            List of recipe dictionaries with complete AI-generated content
        """
        if not self.user_profile:
            raise ValueError("User profile not set. Call collect_user_profile() first.")
        
        # Generate complete recipes directly from AI
        recipes = self._get_ai_generated_recipes(user_request, num_recipes)
        
        # Save recipe request to history if enabled
        if self.save_data and self.storage and recipes:
            self.storage.save_recipe_request(user_request, recipes)
        
        return recipes
    
    
    def _get_ai_generated_recipes(self, user_request: str, num_recipes: int) -> List[Dict]:
        """Generate complete AI recipes without URLs."""
        # Create the prompt for OpenAI
        prompt = self._create_recipe_prompt(user_request, num_recipes)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are PantryVision, a helpful AI assistant that recommends recipes based on user preferences, fitness goals, and dietary restrictions. Always provide practical, delicious recipes with clear instructions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse the response
            recipe_text = response.choices[0].message.content
            recipes = self._parse_recipe_response(recipe_text, num_recipes)
            
            return recipes
            
        except Exception as e:
            print(f"ERROR: Error getting AI-generated recipes: {e}")
            return []
    
    def _create_recipe_prompt(self, user_request: str, num_recipes: int) -> str:
        """Create a detailed prompt for recipe recommendations."""
        profile = self.user_profile
        
        # Create smart context for preferences
        smart_context = self.preference_matcher.create_smart_prompt_context(
            profile.preferences, 
            profile.fitness_goals, 
            user_request
        )
        
        prompt = f"""
Please recommend {num_recipes} recipes based on this request: "{user_request}"

User Profile:
- Allergies: {', '.join(profile.allergies) if profile.allergies else 'None'}
- Dietary Restrictions: {', '.join(profile.dietary_restrictions) if profile.dietary_restrictions else 'None'}
- Smart Context: {smart_context}

For each recipe, provide:
1. Recipe name
2. Brief description (1-2 sentences)
3. Complete ingredients list (8-12 ingredients with quantities)
4. Step-by-step cooking instructions (4-6 clear steps)
5. Preparation time (specific minutes)
6. Cooking time (specific minutes)
7. Detailed nutrition information (calories, protein, carbs, fat, fiber - if estimated, state "estimated")
8. Why this recipe fits their profile (only mention relevant preferences/goals)

Format the response as a JSON array with this structure:
[
  {{
    "name": "Recipe Name",
    "description": "Brief description",
    "ingredients": ["1 lb chicken breast", "2 tbsp olive oil", "1 onion, diced", ...],
    "instructions": ["Step 1: Heat oil in a large pan", "Step 2: Season the chicken", "Step 3: Cook for 6-8 minutes per side", ...],
    "prep_time": "15 minutes",
    "cook_time": "25 minutes",
    "nutrition": "Calories: 350 (estimated), Protein: 28g, Carbs: 12g, Fat: 18g, Fiber: 3g",
    "why_recommended": "Why this fits their profile (only relevant aspects)"
  }}
]

CRITICAL REQUIREMENTS:
- DO NOT include any URLs or source references
- Only apply preferences that make sense for the recipe type (e.g., don't make desserts spicy)
- ALWAYS include complete nutrition information (if estimated, clearly state "estimated")
- ALWAYS include specific prep and cook times
- ALWAYS include detailed ingredients with quantities
- ALWAYS include step-by-step cooking instructions (4-6 clear steps)
- Avoid any ingredients the user is allergic to
- Respect dietary restrictions
- Provide practical, achievable recipes
- Be smart about which preferences apply to which recipe types
"""
        return prompt
    
    def _parse_recipe_response(self, response_text: str, expected_count: int) -> List[Dict]:
        """Parse the OpenAI response into structured recipe data."""
        try:
            # Try to extract JSON from the response
            import re
            
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                recipes = json.loads(json_str)
                
                # Ensure we have the expected number of recipes
                if len(recipes) >= expected_count:
                    return recipes[:expected_count]
                else:
                    return recipes
            else:
                # Fallback: create a simple structure from text
                return self._fallback_parse(response_text, expected_count)
                
        except json.JSONDecodeError:
            # Fallback parsing if JSON parsing fails
            return self._fallback_parse(response_text, expected_count)
    
    def _fallback_parse(self, response_text: str, expected_count: int) -> List[Dict]:
        """Fallback parsing when JSON parsing fails."""
        recipes = []
        lines = response_text.split('\n')
        
        current_recipe = {}
        for line in lines:
            line = line.strip()
            if line.startswith('Recipe') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                if current_recipe:
                    recipes.append(current_recipe)
                current_recipe = {
                    "name": line, 
                    "description": "", 
                    "ingredients": [], 
                    "instructions": [],
                    "prep_time": "", 
                    "cook_time": "", 
                    "nutrition": "", 
                    "why_recommended": ""
                }
            elif line.startswith('Description:'):
                current_recipe["description"] = line.replace('Description:', '').strip()
            elif line.startswith('Ingredients:'):
                current_recipe["ingredients"] = [line.replace('Ingredients:', '').strip()]
            elif line.startswith('Instructions:'):
                current_recipe["instructions"] = [line.replace('Instructions:', '').strip()]
            elif line.startswith('Prep time:'):
                current_recipe["prep_time"] = line.replace('Prep time:', '').strip()
            elif line.startswith('Cook time:'):
                current_recipe["cook_time"] = line.replace('Cook time:', '').strip()
            elif line.startswith('Nutrition:'):
                current_recipe["nutrition"] = line.replace('Nutrition:', '').strip()
            elif line.startswith('Why recommended:'):
                current_recipe["why_recommended"] = line.replace('Why recommended:', '').strip()
        
        if current_recipe:
            recipes.append(current_recipe)
        
        return recipes[:expected_count]
    
    
    def display_recipes(self, recipes: List[Dict]):
        """Display recipes in a formatted way."""
        if not recipes:
            print("ERROR: No recipes found. Please try a different request.")
            return
        
        print(f"\nHere are {len(recipes)} recipe recommendations for you!")
        print("=" * 60)
        
        for i, recipe in enumerate(recipes, 1):
            print(f"\nRecipe {i}: {recipe.get('name', 'Unknown Recipe')}")
            print("-" * 50)
            
            # Description
            if recipe.get('description'):
                print(f"Description: {recipe['description']}")
            
            # Ingredients (always show)
            if recipe.get('ingredients'):
                print(f"\nIngredients:")
                for ingredient in recipe['ingredients']:
                    print(f"  • {ingredient}")
            else:
                print(f"\nIngredients: Not specified")
            
            # Instructions (always show)
            if recipe.get('instructions'):
                print(f"\nInstructions:")
                for i, instruction in enumerate(recipe['instructions'], 1):
                    print(f"  {i}. {instruction}")
            else:
                print(f"\nInstructions: Not provided")
            
            # Prep and Cook Time (always show)
            times = []
            if recipe.get('prep_time'):
                times.append(f"Prep: {recipe['prep_time']}")
            if recipe.get('cook_time'):
                times.append(f"Cook: {recipe['cook_time']}")
            
            if times:
                print(f"\nTime: {', '.join(times)}")
            else:
                print(f"\nTime: Not specified")
            
            # Nutrition (always show)
            if recipe.get('nutrition'):
                print(f"\nNutrition: {recipe['nutrition']}")
            else:
                print(f"\nNutrition: Not specified")
            
            
            # Why recommended
            if recipe.get('why_recommended'):
                print(f"\nWhy recommended: {recipe['why_recommended']}")
            
            print()
    
    def get_user_stats(self) -> Dict[str, any]:
        """Get user statistics from local storage."""
        if self.save_data and self.storage:
            return self.storage.get_user_stats()
        else:
            return {"error": "Data storage not enabled"}
    
    def clear_user_data(self) -> bool:
        """Clear all user data from local storage."""
        if self.save_data and self.storage:
            success = self.storage.clear_user_data()
            if success:
                self.user_profile = None
                print("User data cleared successfully.")
            return success
        else:
            print("Data storage not enabled.")
            return False
    
    def get_model_info(self) -> Dict[str, any]:
        """Get current model configuration."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "save_data": self.save_data,
            "data_dir": self.data_dir
        }
