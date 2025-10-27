"""
PantryVision Smart Preference Matching Module

Handles intelligent matching of user preferences to recipes.
"""

from typing import List, Dict, Set
import re


class SmartPreferenceMatcher:
    """Handles intelligent matching of user preferences to recipes."""
    
    def __init__(self):
        """Initialize the preference matcher."""
        
        # Categories where certain preferences don't apply
        self.preference_categories = {
            "spicy": {
                "incompatible": ["dessert", "cake", "cookie", "ice cream", "pudding", "muffin", "pancake", "waffle"],
                "compatible": ["main", "dinner", "lunch", "appetizer", "soup", "stir-fry", "curry", "pasta", "rice"]
            },
            "meat": {
                "incompatible": ["vegetarian", "vegan", "salad"],
                "compatible": ["main", "dinner", "lunch", "sandwich", "burger", "steak", "chicken", "pork", "beef"]
            },
            "vegetarian": {
                "incompatible": ["meat", "chicken", "beef", "pork", "fish", "seafood"],
                "compatible": ["salad", "vegetable", "pasta", "rice", "soup", "main", "dinner", "lunch"]
            },
            "high_protein": {
                "incompatible": ["dessert", "cake", "cookie", "ice cream", "pudding"],
                "compatible": ["main", "dinner", "lunch", "breakfast", "snack", "smoothie"]
            },
            "low_calorie": {
                "incompatible": ["dessert", "cake", "cookie", "ice cream", "fried", "deep-fried"],
                "compatible": ["salad", "soup", "grilled", "baked", "steamed", "main", "dinner", "lunch"]
            }
        }
        
        # Recipe type keywords
        self.recipe_types = {
            "dessert": ["cake", "cookie", "pie", "tart", "muffin", "cupcake", "brownie", "pudding", "ice cream", "sorbet", "mousse", "cheesecake", "donut", "pancake", "waffle", "crepe"],
            "main": ["dinner", "lunch", "main course", "entree", "meal"],
            "appetizer": ["appetizer", "starter", "hors d'oeuvre", "snack"],
            "soup": ["soup", "stew", "chowder", "broth"],
            "salad": ["salad", "coleslaw", "slaw"],
            "breakfast": ["breakfast", "brunch", "morning"],
            "beverage": ["drink", "beverage", "smoothie", "juice", "cocktail", "mocktail"]
        }
    
    def get_relevant_preferences(self, user_preferences: List[str], recipe_name: str, recipe_description: str = "") -> List[str]:
        """
        Get preferences that are relevant to the specific recipe.
        
        Args:
            user_preferences: List of user's preferences
            recipe_name: Name of the recipe
            recipe_description: Description of the recipe
            
        Returns:
            List of relevant preferences for this recipe
        """
        recipe_text = f"{recipe_name} {recipe_description}".lower()
        relevant_preferences = []
        
        for preference in user_preferences:
            preference_lower = preference.lower()
            
            # Check if preference is relevant to this recipe
            if self._is_preference_relevant(preference_lower, recipe_text):
                relevant_preferences.append(preference)
        
        return relevant_preferences
    
    def get_relevant_fitness_goals(self, fitness_goals: List[str], recipe_name: str, recipe_description: str = "") -> List[str]:
        """
        Get fitness goals that are relevant to the specific recipe.
        
        Args:
            fitness_goals: List of user's fitness goals
            recipe_name: Name of the recipe
            recipe_description: Description of the recipe
            
        Returns:
            List of relevant fitness goals for this recipe
        """
        recipe_text = f"{recipe_name} {recipe_description}".lower()
        relevant_goals = []
        
        for goal in fitness_goals:
            goal_lower = goal.lower()
            
            # Check if fitness goal is relevant to this recipe
            if self._is_fitness_goal_relevant(goal_lower, recipe_text):
                relevant_goals.append(goal)
        
        return relevant_goals
    
    def _is_preference_relevant(self, preference: str, recipe_text: str) -> bool:
        """Check if a preference is relevant to a recipe."""
        
        # Check if preference has category restrictions
        for pref_key, categories in self.preference_categories.items():
            if pref_key in preference:
                # Check incompatible categories
                for incompatible in categories["incompatible"]:
                    if incompatible in recipe_text:
                        return False
                
                # Check compatible categories
                for compatible in categories["compatible"]:
                    if compatible in recipe_text:
                        return True
        
        # Default: preference is relevant if not explicitly incompatible
        return True
    
    def _is_fitness_goal_relevant(self, goal: str, recipe_text: str) -> bool:
        """Check if a fitness goal is relevant to a recipe."""
        
        # High protein goals are not relevant for desserts
        if "protein" in goal and any(dessert in recipe_text for dessert in self.recipe_types["dessert"]):
            return False
        
        # Low calorie goals are not relevant for desserts or fried foods
        if "calorie" in goal and any(incompatible in recipe_text for incompatible in ["dessert", "cake", "cookie", "fried", "deep-fried"]):
            return False
        
        # Muscle building goals are not relevant for desserts
        if "muscle" in goal and any(dessert in recipe_text for dessert in self.recipe_types["dessert"]):
            return False
        
        return True
    
    def create_smart_prompt_context(self, user_preferences: List[str], fitness_goals: List[str], 
                                  recipe_name: str, recipe_description: str = "") -> str:
        """
        Create smart context for the AI prompt based on recipe type.
        
        Args:
            user_preferences: List of user's preferences
            fitness_goals: List of user's fitness goals
            recipe_name: Name of the recipe
            recipe_description: Description of the recipe
            
        Returns:
            Smart context string for the AI prompt
        """
        recipe_text = f"{recipe_name} {recipe_description}".lower()
        
        # Get relevant preferences and goals
        relevant_preferences = self.get_relevant_preferences(user_preferences, recipe_name, recipe_description)
        relevant_goals = self.get_relevant_fitness_goals(fitness_goals, recipe_name, recipe_description)
        
        context_parts = []
        
        if relevant_preferences:
            context_parts.append(f"Relevant preferences: {', '.join(relevant_preferences)}")
        
        if relevant_goals:
            context_parts.append(f"Relevant fitness goals: {', '.join(relevant_goals)}")
        
        # Add recipe type context
        recipe_type = self._get_recipe_type(recipe_text)
        if recipe_type:
            context_parts.append(f"Recipe type: {recipe_type}")
        
        return ". ".join(context_parts) if context_parts else "No specific preferences apply to this recipe type."
    
    def _get_recipe_type(self, recipe_text: str) -> str:
        """Determine the type of recipe."""
        for recipe_type, keywords in self.recipe_types.items():
            if any(keyword in recipe_text for keyword in keywords):
                return recipe_type
        return "main"
