"""
Test script for admin functionality including database operations.
"""
import os
import json
from pathlib import Path
from ecommerce_agents.admin import AdminAPI, UpdateSettingsRequest

def test_admin_crud():
    """Test Create, Read, Update, Delete operations for admin settings."""
    
    # Setup: Create a test settings file
    test_settings_file = "test_settings.json"
    if os.path.exists(test_settings_file):
        os.remove(test_settings_file)
    
    # Initialize API
    api = AdminAPI()
    
    print("\n=== Testing Admin Settings API ===\n")
    
    # Test 1: Initial Settings
    print("1. Testing Initial Settings...")
    settings = api.get_settings()
    assert settings["name"] == "", "Initial name should be empty"
    assert settings["target_countries"] == [], "Initial target_countries should be empty"
    print("✓ Initial settings are empty as expected")
    
    # Test 2: Update Personal Info
    print("\n2. Testing Personal Info Update...")
    updates = UpdateSettingsRequest(
        name="John",
        first_name="Doe"
    )
    updated = api.update_settings(updates)
    assert updated["name"] == "John", "Name not updated correctly"
    assert updated["first_name"] == "Doe", "First name not updated correctly"
    print("✓ Personal info updated successfully")
    
    # Test 3: Update Business Info
    print("\n3. Testing Business Info Update...")
    updates = UpdateSettingsRequest(
        business_name="Tech Store",
        target_countries=["USA", "Canada"],
        competitors=["CompA", "CompB"],
        main_urls=["https://techstore.com"]
    )
    updated = api.update_settings(updates)
    assert updated["business_name"] == "Tech Store", "Business name not updated"
    assert "USA" in updated["target_countries"], "Target countries not updated"
    print("✓ Business info updated successfully")
    
    # Test 4: Save and Load
    print("\n4. Testing Save and Load...")
    success = api.save_settings()
    assert success, "Failed to save settings"
    
    # Create new API instance to test loading
    new_api = AdminAPI()
    loaded = new_api.get_settings()
    assert loaded["name"] == "John", "Loaded name doesn't match"
    assert loaded["business_name"] == "Tech Store", "Loaded business name doesn't match"
    print("✓ Settings saved and loaded successfully")
    
    # Test 5: Reset Settings
    print("\n5. Testing Reset...")
    reset = api.reset_settings()
    assert reset["name"] == "", "Name not reset"
    assert reset["business_name"] == "", "Business name not reset"
    assert reset["target_countries"] == [], "Target countries not reset"
    print("✓ Settings reset successfully")
    
    print("\n✓ All admin tests passed successfully!")

def display_current_settings(api):
    """Helper function to display current settings."""
    settings = api.get_settings()
    print("\nCurrent Settings:")
    print("-" * 20)
    for key, value in settings.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(value) if value else 'Empty'}")
        else:
            print(f"{key}: {value if value else 'Empty'}")

if __name__ == "__main__":
    test_admin_crud()