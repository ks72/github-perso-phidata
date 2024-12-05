import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ecommerce_agents.admin.admin_menu import AdminMenu

async def run_admin_menu():
    # 1. Create the admin menu
    menu = AdminMenu()
    
    try:
        # 2. Set up a user (this creates a new user if ID not provided)
        user_id = await menu.set_user_id()
        print(f"Using user ID: {user_id}")
        
        # 3. Now we can use the menu
        while True:
            try:
                # Display menu options
                menu_text = await menu.display_menu()
                print(menu_text)
                
                # Get user choice
                choice = input().strip()
                
                # Handle the choice
                continue_loop, message = await menu.handle_input(choice)
                print(message)
                
                if not continue_loop:
                    break
            except EOFError:
                print("\nExiting due to EOF")
                break
            except KeyboardInterrupt:
                print("\nExiting due to user interrupt")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
    
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the async menu
    sys.exit(asyncio.run(run_admin_menu()))
