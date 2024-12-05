from typing import Dict, Any, Optional
from .api import AdminAPI, UpdateSettingsRequest

class AdminMenu:
    def __init__(self, db_file: str = "tmp/admin.db"):
        """Initialize the admin menu with storage backend."""
        self.api = AdminAPI(db_file=db_file)
        self._current_user_id: Optional[str] = None

    @property
    def current_user_id(self) -> str:
        """Get current user ID, creating one if needed."""
        if self._current_user_id is None:
            raise ValueError("No user ID set. Call set_user_id() first.")
        return self._current_user_id

    async def set_user_id(self, user_id: Optional[str] = None) -> str:
        """Set or create user ID for the session."""
        if user_id is None:
            user_id = await self.api.create_user()
        self._current_user_id = user_id
        return user_id

    async def get_settings(self) -> Dict[str, Any]:
        """Get settings for current user."""
        settings = await self.api.get_settings(self.current_user_id)
        return settings.dict()

    async def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update settings for current user."""
        settings = await self.api.update_settings(self.current_user_id, updates)
        return settings.dict()

    async def display_menu(self) -> str:
        menu = """
=== Admin Settings Menu ===
1. Update Personal Info
2. Update Business Info
3. Update Target Countries
4. Update Competitors
5. Update Main URLs
6. Display Current Settings
7. Save Changes
8. Reset Settings
9. Exit

Choose an option (1-9): """
        return menu

    async def handle_input(self, choice: str) -> tuple[bool, str]:
        handlers = {
            "1": self._update_personal_info,
            "2": self._update_business_info,
            "3": self._update_target_countries,
            "4": self._update_competitors,
            "5": self._update_main_urls,
            "6": self._display_settings,
            "7": self._save_settings,
            "8": self._reset_settings,
            "9": self._exit_menu
        }
        
        handler = handlers.get(choice)
        if handler:
            return await handler()
        return True, "Invalid option. Please try again."

    async def _update_personal_info(self) -> tuple[bool, str]:
        name = input("Enter your name (or press Enter to skip): ").strip()
        first_name = input("Enter your first name (or press Enter to skip): ").strip()
        
        updates = UpdateSettingsRequest(
            name=name if name else None,
            first_name=first_name if first_name else None
        )
        await self.update_settings(updates.dict())
        return True, "Personal info updated."

    async def _update_business_info(self) -> tuple[bool, str]:
        business_name = input("Enter your business name: ").strip()
        if business_name:
            updates = UpdateSettingsRequest(business_name=business_name)
            await self.update_settings(updates.dict())
        return True, "Business info updated."

    async def _update_target_countries(self) -> tuple[bool, str]:
        print("Enter target countries (one per line, empty line to finish):")
        countries = []
        while True:
            country = input().strip()
            if not country:
                break
            countries.append(country)
        
        if countries:
            updates = UpdateSettingsRequest(target_countries=countries)
            await self.update_settings(updates.dict())
        return True, f"{len(countries)} target countries updated."

    async def _update_competitors(self) -> tuple[bool, str]:
        print("Enter competitors (one per line, empty line to finish):")
        competitors = []
        while True:
            competitor = input().strip()
            if not competitor:
                break
            competitors.append(competitor)
        
        if competitors:
            updates = UpdateSettingsRequest(competitors=competitors)
            await self.update_settings(updates.dict())
        return True, f"{len(competitors)} competitors updated."

    async def _update_main_urls(self) -> tuple[bool, str]:
        print("Enter main URLs (one per line, empty line to finish):")
        urls = []
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)
        
        if urls:
            updates = UpdateSettingsRequest(main_urls=urls)
            await self.update_settings(updates.dict())
        return True, f"{len(urls)} URLs updated."

    async def _display_settings(self) -> tuple[bool, str]:
        settings = await self.get_settings()
        settings_str = f"""
Current Settings:
----------------
Name: {settings['name']}
First Name: {settings['first_name']}
Business Name: {settings['business_name']}
Target Countries: {', '.join(settings['target_countries'])}
Competitors: {', '.join(settings['competitors'])}
Main URLs: {', '.join(settings['main_urls'])}
"""
        return True, settings_str

    async def _save_settings(self) -> tuple[bool, str]:
        success = await self.api.save_settings(self.current_user_id)
        return True, "Settings saved successfully." if success else "Failed to save settings."

    async def _reset_settings(self) -> tuple[bool, str]:
        await self.api.reset_settings(self.current_user_id)
        return True, "Settings reset to default values."

    async def _exit_menu(self) -> tuple[bool, str]:
        return False, "Exiting admin menu."
