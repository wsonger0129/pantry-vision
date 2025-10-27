"""
PantryVision Terminal Interface

Interactive terminal interface for the PantryVision AI Recipe Agent.
"""

import os
import sys
from typing import Optional
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.recipe_agent import RecipeAgent, UserProfile

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Load environment variables
load_dotenv()


class PantryVisionTerminal:
    """Terminal interface for PantryVision AI Recipe Agent."""
    
    def __init__(self):
        self.agent: Optional[RecipeAgent] = None
        self.is_running = False
        
    def start(self):
        """Start the PantryVision terminal interface."""
        self.is_running = True
        
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Welcome to PantryVision - Your AI Recipe Assistant!")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Initialize the agent
        try:
            self._initialize_agent()
        except ValueError as e:
            print(f"{Fore.RED}ERROR: {e}")
            print(f"{Fore.YELLOW}Please set your OpenAI API key:")
            print(f"{Fore.YELLOW}   1. Create a .env file in the project root")
            print(f"{Fore.YELLOW}   2. Add: OPENAI_API_KEY=your_api_key_here")
            print(f"{Fore.YELLOW}   3. Or pass it directly when prompted")
            return
        
        # Collect user profile on first run
        if not self.agent.user_profile:
            self.agent.collect_user_profile()
        
        # Main interaction loop
        self._main_loop()
    
    def _initialize_agent(self):
        """Initialize the RecipeAgent with API key."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print(f"{Fore.YELLOW}🔑 OpenAI API key not found in environment variables.")
            api_key = input(f"{Fore.CYAN}Please enter your OpenAI API key: ").strip()
            
            if not api_key:
                raise ValueError("OpenAI API key is required to use PantryVision.")
        
        self.agent = RecipeAgent(api_key=api_key)
        print(f"{Fore.GREEN}SUCCESS: PantryVision AI Agent initialized successfully!")
        
        # Show model configuration
        model_info = self.agent.get_model_info()
        print(f"{Fore.CYAN}Model Configuration:")
        print(f"  Model: {model_info['model']}")
        print(f"  Max Tokens: {model_info['max_tokens']}")
        print(f"  Temperature: {model_info['temperature']}")
        print(f"  Data Storage: {'Enabled' if model_info['save_data'] else 'Disabled'}")
        if model_info['save_data']:
            print(f"  Data Directory: {model_info['data_dir']}")
    
    def _main_loop(self):
        """Main interaction loop."""
        print(f"\n{Fore.GREEN}PantryVision is ready! Type your requests or 'help' for commands.")
        print(f"{Fore.CYAN}Example: 'I want meat for dinner tonight' or 'vegetarian lunch ideas'")
        
        while self.is_running:
            try:
                user_input = input(f"\n{Fore.CYAN}You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self._handle_quit()
                elif user_input.lower() in ['help', 'h']:
                    self._show_help()
                elif user_input.lower() in ['profile', 'p']:
                    self._handle_profile_update()
                elif user_input.lower() in ['stats', 's']:
                    self._handle_user_stats()
                elif user_input.lower() in ['clear', 'c']:
                    os.system('cls' if os.name == 'nt' else 'clear')
                elif user_input.lower() in ['reset', 'r']:
                    self._handle_reset_data()
                else:
                    self._handle_recipe_request(user_input)
                    
            except KeyboardInterrupt:
                self._handle_quit()
            except Exception as e:
                print(f"{Fore.RED}ERROR: An error occurred: {e}")
                print(f"{Fore.YELLOW}Please try again or type 'help' for assistance.")
    
    def _handle_recipe_request(self, request: str):
        """Handle a recipe recommendation request."""
        print(f"{Fore.YELLOW}PantryVision: Let me find some great recipes for you...")
        
        try:
            recipes = self.agent.get_recipe_recommendations(request)
            self.agent.display_recipes(recipes)
            
            if recipes:
                print(f"{Fore.GREEN}Tip: You can ask for more specific recipes or update your profile anytime!")
            
        except Exception as e:
            print(f"{Fore.RED}Sorry, I couldn't process that request: {e}")
            print(f"{Fore.YELLOW}Try rephrasing your request or type 'help' for examples.")
    
    def _handle_profile_update(self):
        """Handle profile update request."""
        print(f"{Fore.CYAN}Let's update your profile!")
        self.agent.collect_user_profile()
    
    def _handle_user_stats(self):
        """Handle user statistics request."""
        print(f"{Fore.CYAN}User Statistics:")
        print("-" * 30)
        stats = self.agent.get_user_stats()
        
        if "error" in stats:
            print(f"{Fore.RED}{stats['error']}")
        else:
            print(f"Profile Created: {stats['profile_created']}")
            print(f"Last Updated: {stats['last_updated']}")
            print(f"Total Recipes Requested: {stats['total_recipes_requested']}")
            print(f"Total Requests: {stats['total_requests']}")
            print(f"\nCurrent Profile:")
            print(f"  Preferences: {', '.join(stats['preferences']) if stats['preferences'] else 'None'}")
            print(f"  Fitness Goals: {', '.join(stats['fitness_goals']) if stats['fitness_goals'] else 'None'}")
            print(f"  Allergies: {', '.join(stats['allergies']) if stats['allergies'] else 'None'}")
            print(f"  Dietary Restrictions: {', '.join(stats['dietary_restrictions']) if stats['dietary_restrictions'] else 'None'}")
    
    def _handle_reset_data(self):
        """Handle data reset request."""
        print(f"{Fore.YELLOW}Are you sure you want to clear all your data? (yes/no): ", end="")
        confirm = input().strip().lower()
        
        if confirm in ['yes', 'y']:
            if self.agent.clear_user_data():
                print(f"{Fore.GREEN}All user data has been cleared.")
            else:
                print(f"{Fore.RED}Failed to clear user data.")
        else:
            print(f"{Fore.CYAN}Data reset cancelled.")
    
    def _show_help(self):
        """Show help information."""
        print(f"\n{Fore.CYAN}PantryVision Help")
        print(f"{Fore.CYAN}{'='*30}")
        print(f"{Fore.WHITE}Available commands:")
        print(f"  {Fore.GREEN}help, h{Fore.WHITE}     - Show this help message")
        print(f"  {Fore.GREEN}profile, p{Fore.WHITE}  - Update your preferences and goals")
        print(f"  {Fore.GREEN}stats, s{Fore.WHITE}    - Show your usage statistics")
        print(f"  {Fore.GREEN}clear, c{Fore.WHITE}    - Clear the screen")
        print(f"  {Fore.GREEN}reset, r{Fore.WHITE}    - Clear all your saved data")
        print(f"  {Fore.GREEN}quit, exit, q{Fore.WHITE} - Exit PantryVision")
        print(f"\n{Fore.WHITE}Example requests:")
        print(f"  {Fore.YELLOW}• 'I want meat for dinner tonight'")
        print(f"  {Fore.YELLOW}• 'vegetarian lunch ideas'")
        print(f"  {Fore.YELLOW}• 'high protein breakfast'")
        print(f"  {Fore.YELLOW}• 'low calorie snacks'")
        print(f"  {Fore.YELLOW}• 'quick 30-minute meals'")
        print(f"  {Fore.YELLOW}• 'comfort food for a cold day'")
        print(f"\n{Fore.CYAN}PantryVision considers your:")
        print(f"  • Food preferences")
        print(f"  • Fitness goals")
        print(f"  • Allergies and dietary restrictions")
    
    def _handle_quit(self):
        """Handle quit request."""
        print(f"\n{Fore.CYAN}Thanks for using PantryVision!")
        print(f"{Fore.CYAN}Happy cooking!")
        self.is_running = False


def main():
    """Main entry point for the terminal interface."""
    try:
        app = PantryVisionTerminal()
        app.start()
    except Exception as e:
        print(f"{Fore.RED}ERROR: Failed to start PantryVision: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()