"""
Admin panel component for configuring the eCommerce trend analysis system.
"""
from typing import Dict, Optional
import streamlit as st
import json
import os

class AdminPanel:
    def __init__(self):
        self.config_file = "admin_config.json"
        self._init_session_state()
        
    def _init_session_state(self):
        """Initialize session state variables."""
        if 'admin_config' not in st.session_state:
            st.session_state.admin_config = self.load_config()
            
    def load_config(self) -> Dict:
        """Load configuration from file."""
        default_config = {
            "business_name": "",
            "owner_name": "",
            "owner_first_name": "",
            "main_urls": [],
            "target_countries": [],
            "competitors": []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return default_config
        return default_config
    
    def save_config(self, config: Dict):
        """Save configuration to file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
    def display_panel(self):
        """Display the admin panel interface."""
        st.title("Admin Configuration Panel")
        
        config = st.session_state.admin_config
        
        # Business Information
        st.header("Business Information")
        config["business_name"] = st.text_input("Business Name", config["business_name"])
        config["owner_name"] = st.text_input("Owner Last Name", config["owner_name"])
        config["owner_first_name"] = st.text_input("Owner First Name", config["owner_first_name"])
        
        # URLs
        st.header("URLs")
        urls_str = "\n".join(config["main_urls"])
        new_urls = st.text_area("Main URLs (one per line)", urls_str)
        config["main_urls"] = [url.strip() for url in new_urls.split("\n") if url.strip()]
        
        # Target Countries
        st.header("Target Countries")
        countries_str = "\n".join(config["target_countries"])
        new_countries = st.text_area("Target Countries (one per line)", countries_str)
        config["target_countries"] = [country.strip() for country in new_countries.split("\n") if country.strip()]
        
        # Competitors
        st.header("Competitors")
        competitors_str = "\n".join(config["competitors"])
        new_competitors = st.text_area("Competitors (one per line)", competitors_str)
        config["competitors"] = [comp.strip() for comp in new_competitors.split("\n") if comp.strip()]
        
        # Save button
        if st.button("Save Configuration"):
            self.save_config(config)
            st.success("Configuration saved successfully!")
            
    def get_config(self) -> Dict:
        """Get the current configuration."""
        return st.session_state.admin_config
