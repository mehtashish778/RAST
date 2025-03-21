# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Main Application
"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add the app directory to the path so we can import modules
app_dir = Path(__file__).parent.absolute()
sys.path.append(str(app_dir))

# Import page modules
from pages.home import render_home_page
from pages.chemicals import render_chemical_database_page
from pages.equipment import render_equipment_database_page

# Import utility modules
from utils.database import get_db_manager
from utils.init_db import init_database

def setup_streamlit():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="HAZOP Analysis Tool",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def initialize_app():
    """Initialize application database and resources"""
    # Initialize database if not already done
    if 'db_initialized' not in st.session_state:
        with st.spinner("Initializing database..."):
            db_manager = get_db_manager()
            if not db_manager.connect():
                st.error("Failed to connect to database")
                return False
            
            # Initialize database schema
            init_database()
            
            st.session_state.db_initialized = True
    
    return st.session_state.db_initialized

def main():
    """Main application entry point"""
    # Configure Streamlit settings
    setup_streamlit()
    
    # Initialize application
    if not initialize_app():
        st.error("Application failed to initialize properly. Please check the logs.")
        return
    
    # Initialize session state for navigation if it doesn't exist
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # App header
    st.title("HAZOP Analysis Tool")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = ["Home", "Chemical Database", "Equipment Database"]
    selected_page = st.sidebar.radio("Select Page", pages, index=pages.index(st.session_state.current_page))
    
    # Update session state
    st.session_state.current_page = selected_page
    
    # Render the selected page
    if selected_page == "Home":
        render_home_page()
    elif selected_page == "Chemical Database":
        render_chemical_database_page()
    elif selected_page == "Equipment Database":
        render_equipment_database_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("HAZOP Analysis Tool v0.1.0")

if __name__ == "__main__":
    main()
