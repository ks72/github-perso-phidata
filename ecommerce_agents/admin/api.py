from typing import List, Dict, Any
from .settings import AdminSettings, AdminStorage
from pydantic import BaseModel

class UpdateSettingsRequest(BaseModel):
    name: str | None = None
    first_name: str | None = None
    business_name: str | None = None
    target_countries: List[str] | None = None
    competitors: List[str] | None = None
    main_urls: List[str] | None = None

class AdminAPI:
    """API layer for admin settings management.
    This class provides a clean interface that can be used by any frontend (CLI, Web, etc.)
    """
    def __init__(self, db_file: str = "tmp/admin.db"):
        """Initialize the Admin API with storage backend."""
        self.storage = AdminStorage(db_file=db_file)

    async def create_user(self) -> str:
        """Create a new user and return their ID."""
        user_id = self.storage.generate_user_id()
        settings = AdminSettings(user_id=user_id)
        await self.storage.save_settings(settings)
        return user_id

    async def get_settings(self, user_id: str) -> AdminSettings:
        """Get settings for a specific user."""
        return await self.storage.get_settings(user_id)

    async def update_settings(self, user_id: str, updates: UpdateSettingsRequest) -> AdminSettings:
        """Update settings for a specific user."""
        settings = await self.storage.get_settings(user_id)
        update_dict = updates.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        await self.storage.save_settings(settings)
        return settings

    async def delete_user(self, user_id: str) -> None:
        """Delete a user's settings."""
        await self.storage.delete_settings(user_id)

    async def reset_settings(self, user_id: str) -> AdminSettings:
        """Reset settings to default values for a specific user."""
        settings = AdminSettings(
            user_id=user_id,
            name="",
            first_name="",
            business_name="",
            target_countries=[],
            competitors=[],
            main_urls=[]
        )
        await self.storage.save_settings(settings)
        return settings
