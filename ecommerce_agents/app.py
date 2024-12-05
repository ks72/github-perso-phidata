"""
Main application file for the eCommerce trend analysis system.
"""
import streamlit as st
from ui.chat_interface import ChatInterface
from ui.admin_panel import AdminPanel

def main():
    st.set_page_config(
        page_title="eCommerce Trend Analysis",
        page_icon="🛍️",
        layout="wide"
    )
    
    # Initialize components
    chat = ChatInterface()
    admin = AdminPanel()
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Chat", "Admin Panel"])
    
    if page == "Chat":
        chat.display_chat()
        
        # Add a clear chat button to the sidebar
        if st.sidebar.button("Clear Chat History"):
            chat.clear_chat()
            st.experimental_rerun()
            
    else:  # Admin Panel
        admin.display_panel()

if __name__ == "__main__":
    main()
