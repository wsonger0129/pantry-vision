#!/usr/bin/env python3
"""
Test script for PantryVision AI Recipe Agent

This script tests the basic functionality without requiring user interaction.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ai.recipe_agent import RecipeAgent, UserProfile
    print("SUCCESS: Successfully imported RecipeAgent")
except ImportError as e:
    print(f"ERROR: Failed to import RecipeAgent: {e}")
    sys.exit(1)


def test_user_profile():
    """Test UserProfile creation."""
    print("\nTESTING: UserProfile creation...")
    
    profile = UserProfile(
        preferences=["love meat", "spicy food"],
        fitness_goals=["high protein", "muscle building"],
        allergies=["nuts"],
        dietary_restrictions=["keto"]
    )
    
    print(f"SUCCESS: Created profile with:")
    print(f"   Preferences: {profile.preferences}")
    print(f"   Fitness goals: {profile.fitness_goals}")
    print(f"   Allergies: {profile.allergies}")
    print(f"   Dietary restrictions: {profile.dietary_restrictions}")


def test_recipe_agent_init():
    """Test RecipeAgent initialization (without API key)."""
    print("\nTESTING: RecipeAgent initialization...")
    
    try:
        # This should fail without API key
        agent = RecipeAgent()
        print("ERROR: Unexpected: Agent initialized without API key")
    except ValueError as e:
        print(f"SUCCESS: Expected error: {e}")
    
    # Test with dummy API key
    try:
        agent = RecipeAgent(api_key="dummy_key")
        print("SUCCESS: Agent initialized with dummy API key")
        return agent
    except Exception as e:
        print(f"ERROR: Unexpected error with dummy key: {e}")
        return None


def test_prompt_creation():
    """Test recipe prompt creation."""
    print("\nTESTING: Recipe prompt creation...")
    
    agent = RecipeAgent(api_key="dummy_key")
    agent.user_profile = UserProfile(
        preferences=["vegetarian"],
        fitness_goals=["low calorie"],
        allergies=["dairy"],
        dietary_restrictions=[]
    )
    
    prompt = agent._create_recipe_prompt("I want a healthy lunch", 2)
    
    print("SUCCESS: Recipe prompt created successfully")
    print(f"   Prompt length: {len(prompt)} characters")
    print(f"   Contains user preferences: {'vegetarian' in prompt}")
    print(f"   Contains fitness goals: {'low calorie' in prompt}")
    print(f"   Contains allergies: {'dairy' in prompt}")


def test_recipe_parsing():
    """Test recipe response parsing."""
    print("\nTESTING: Recipe response parsing...")
    
    agent = RecipeAgent(api_key="dummy_key")
    
    # Test JSON parsing
    json_response = '''
    [
        {
            "name": "Test Recipe",
            "description": "A test recipe",
            "ingredients": ["ingredient1", "ingredient2"],
            "prep_time": "10 minutes",
            "cook_time": "20 minutes",
            "nutrition": "Calories: 300",
            "why_recommended": "Fits your preferences"
        }
    ]
    '''
    
    recipes = agent._parse_recipe_response(json_response, 1)
    
    if recipes and len(recipes) == 1:
        recipe = recipes[0]
        print("SUCCESS: JSON parsing successful")
        print(f"   Recipe name: {recipe.get('name')}")
        print(f"   Ingredients count: {len(recipe.get('ingredients', []))}")
    else:
        print("ERROR: JSON parsing failed")


def main():
    """Run all tests."""
    print("PantryVision AI Agent Test Suite")
    print("=" * 40)
    
    test_user_profile()
    test_recipe_agent_init()
    test_prompt_creation()
    test_recipe_parsing()
    
    print("\nSUCCESS: All tests completed!")
    print("\nTo run the full application:")
    print("   1. Set up your OpenAI API key in .env file")
    print("   2. Run: python src/main.py")


if __name__ == "__main__":
    main()
