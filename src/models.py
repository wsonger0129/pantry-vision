"""
PantryVision User Profile Module

Contains the UserProfile dataclass used across the application.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class UserProfile:
    """User profile containing preferences, goals, and restrictions."""
    preferences: List[str]  # e.g., ["love meat", "vegetarian", "vegan"]
    fitness_goals: List[str]  # e.g., ["high protein", "low cal", "bulking", "cutting"]
    allergies: List[str]  # e.g., ["nuts", "dairy", "gluten"]
    dietary_restrictions: List[str]  # e.g., ["keto", "paleo", "mediterranean"]
