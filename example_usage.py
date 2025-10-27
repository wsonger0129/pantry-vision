#!/usr/bin/env python3
"""
PantryVision Usage Example

This script demonstrates how to use the PantryVision AI Recipe Agent programmatically.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.recipe_agent import RecipeAgent, UserProfile


def example_usage():
    """Demonstrate programmatic usage of the RecipeAgent."""
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("💡 Set OPENAI_API_KEY environment variable or add it to .env file")
        return
    
    print("🍽️  PantryVision AI Recipe Agent - Example Usage")
    print("=" * 50)
    
    # Initialize the agent
    agent = RecipeAgent(api_key=api_key)
    
    # Create a sample user profile
    user_profile = UserProfile(
        preferences=["love meat", "spicy food"],
        fitness_goals=["high protein", "muscle building"],
        allergies=["nuts"],
        dietary_restrictions=["keto"]
    )
    
    agent.user_profile = user_profile
    
    print("👤 Sample User Profile:")
    print(f"   Preferences: {', '.join(user_profile.preferences)}")
    print(f"   Fitness goals: {', '.join(user_profile.fitness_goals)}")
    print(f"   Allergies: {', '.join(user_profile.allergies)}")
    print(f"   Dietary restrictions: {', '.join(user_profile.dietary_restrictions)}")
    
    # Example requests
    requests = [
        "I want meat for dinner tonight",
        "high protein breakfast ideas",
        "keto-friendly lunch"
    ]
    
    for request in requests:
        print(f"\n🤖 Request: '{request}'")
        print("-" * 30)
        
        try:
            recipes = agent.get_recipe_recommendations(request, num_recipes=2)
            agent.display_recipes(recipes)
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    example_usage()
