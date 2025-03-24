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
from pages.scenarios import render_scenarios_page

# Import utility modules
from utils.database import get_db_manager
from utils.init_db import init_database
from utils.navigation import get_nav_manager

# Update the page config at the start of app.py
st.set_page_config(
    page_title="HAZOP Analysis Tool",
    page_icon="🏭",  # Optional: add an icon for your app
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Hide the default Streamlit pages navigation
hide_pages = """
<style>
    [data-testid="stSidebarNav"] {display: none !important;}
</style>
"""
st.markdown(hide_pages, unsafe_allow_html=True)

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

def setup_navigation():
    """Setup navigation with registered pages"""
    nav_manager = get_nav_manager()
    
    # Register pages with icons and order - make Home the default (order=1)
    nav_manager.register_page("Home", render_home_page, "house", 1)
    nav_manager.register_page("Chemical Database", render_chemical_database_page, "flask", 2)
    nav_manager.register_page("Equipment Database", render_equipment_database_page, "gear", 3)
    nav_manager.register_page("Scenarios", render_scenarios_page, "exclamation-triangle", 4)
    
    # Import the release page function dynamically to avoid circular imports
    from pages.release import render_release_calculation_page
    nav_manager.register_page("Release Calculations", render_release_calculation_page, "droplet", 5)

def main():
    """Main application entry point"""
    # Initialize application
    if not initialize_app():
        st.error("Application failed to initialize properly. Please check the logs.")
        return
    
    # Setup navigation
    setup_navigation()
    nav_manager = get_nav_manager()
    
    # Render navigation and get selected page
    selected_page = nav_manager.render_sidebar_navigation()
    
    # Update session state
    st.session_state.current_page = selected_page
    
    # Render the selected page
    nav_manager.render_current_page(selected_page)

if __name__ == "__main__":
    main()
