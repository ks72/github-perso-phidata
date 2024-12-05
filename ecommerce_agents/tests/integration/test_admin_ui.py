"""
Streamlit test app for admin functionality.
"""
import os
import sys
from pathlib import Path

# Add the ecommerce_agents directory to Python path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import asyncio
from admin.admin_menu import AdminMenu  # Using relative import
from admin.api import UpdateSettingsRequest  # Import the request model

# Create necessary directories
os.makedirs("tmp", exist_ok=True)

# Initialize admin menu in session state
if 'admin_menu' not in st.session_state:
    st.session_state.admin_menu = AdminMenu(db_file="tmp/admin.db")

# Initialize user ID in session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = asyncio.run(st.session_state.admin_menu.set_user_id())
    # Explicitly set the user ID in admin_menu
    asyncio.run(st.session_state.admin_menu.set_user_id(st.session_state.user_id))

def main():
    st.title("Admin Menu Test App")
    
    # Display current user ID
    st.sidebar.write(f"Current User ID: {st.session_state.user_id}")
    
    try:
        # Get current settings
        settings = asyncio.run(st.session_state.admin_menu.get_settings())
        # Convert settings to dict if it's not already
        if hasattr(settings, 'model_dump'):  # For Pydantic v2
            settings = settings.model_dump()
        elif hasattr(settings, 'dict'):  # For Pydantic v1
            settings = settings.dict()
        
        # Personal Information Section
        with st.expander("Personal Information", expanded=True):
            name = st.text_input("Name", value=settings.get('name', '') or '')
            first_name = st.text_input("First Name", value=settings.get('first_name', '') or '')
            if st.button("Update Personal Info"):
                request = UpdateSettingsRequest(
                    name=name,
                    first_name=first_name
                )
                asyncio.run(st.session_state.admin_menu.update_settings(request))
                st.success("Personal information updated!")
        
        # Business Information Section
        with st.expander("Business Information", expanded=True):
            business_name = st.text_input("Business Name", value=settings.get('business_name', '') or '')
            if st.button("Update Business Info"):
                request = UpdateSettingsRequest(
                    business_name=business_name
                )
                asyncio.run(st.session_state.admin_menu.update_settings(request))
                st.success("Business information updated!")
        
        # Target Countries Section
        with st.expander("Target Countries", expanded=True):
            countries = st.text_area(
                "Target Countries (one per line)",
                value='\n'.join(settings.get('target_countries', []))
            )
            if st.button("Update Target Countries"):
                country_list = [c.strip() for c in countries.split('\n') if c.strip()]
                request = UpdateSettingsRequest(
                    target_countries=country_list
                )
                asyncio.run(st.session_state.admin_menu.update_settings(request))
                st.success("Target countries updated!")
        
        # Competitors Section
        with st.expander("Competitors", expanded=True):
            competitors = st.text_area(
                "Competitors (one per line)",
                value='\n'.join(settings.get('competitors', []))
            )
            if st.button("Update Competitors"):
                competitor_list = [c.strip() for c in competitors.split('\n') if c.strip()]
                request = UpdateSettingsRequest(
                    competitors=competitor_list
                )
                asyncio.run(st.session_state.admin_menu.update_settings(request))
                st.success("Competitors updated!")
        
        # Main URLs Section
        with st.expander("Main URLs", expanded=True):
            urls = st.text_area(
                "Main URLs (one per line)",
                value='\n'.join(settings.get('main_urls', []))
            )
            if st.button("Update Main URLs"):
                url_list = [u.strip() for u in urls.split('\n') if u.strip()]
                request = UpdateSettingsRequest(
                    main_urls=url_list
                )
                asyncio.run(st.session_state.admin_menu.update_settings(request))
                st.success("Main URLs updated!")
        
        # Settings Management
        st.subheader("Settings Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save All Changes"):
                asyncio.run(st.session_state.admin_menu.api.save_settings(st.session_state.user_id))
                st.success("All changes saved successfully!")
        
        with col2:
            if st.button("Reset Settings"):
                asyncio.run(st.session_state.admin_menu.api.reset_settings(st.session_state.user_id))
                st.success("Settings reset to default values!")
                st.rerun()
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if st.button("Reset User ID"):
            # Create new admin menu and user ID
            st.session_state.admin_menu = AdminMenu(db_file="tmp/admin.db")
            st.session_state.user_id = asyncio.run(st.session_state.admin_menu.set_user_id())
            st.rerun()

if __name__ == "__main__":
    main()
