"""
Chat interface component for the eCommerce trend analysis system.
"""
from typing import Dict, List, Optional
import streamlit as st
from datetime import datetime
import json
import os

class ChatInterface:
    def __init__(self):
        self.history_file = "chat_history.json"
        self._init_session_state()
        
    def _init_session_state(self):
        """Initialize session state variables."""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'language' not in st.session_state:
            st.session_state.language = 'en'  # Default language
            
    def load_chat_history(self) -> List[Dict]:
        """Load chat history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def save_chat_history(self, messages: List[Dict]):
        """Save chat history to file."""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
            
    def display_chat(self):
        """Display the chat interface."""
        st.title("eCommerce Trend Analysis Chat")
        
        # Language selector
        languages = {
            'en': 'English',
            'fr': 'Français',
            'es': 'Español',
            'de': 'Deutsch'
        }
        selected_lang = st.selectbox(
            "Select Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            key="language_selector"
        )
        st.session_state.language = selected_lang
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("What would you like to know about eCommerce trends?"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Save to history
            self.save_chat_history(st.session_state.messages)
            
            # Here we would process the message and get the response
            # This will be connected to the User Query Agent later
            
    def clear_chat(self):
        """Clear the chat history."""
        st.session_state.messages = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
