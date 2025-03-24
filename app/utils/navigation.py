"""
Navigation utility for the HAZOP Analysis Tool
Provides page navigation and routing functionality
"""
import streamlit as st
from typing import Dict, Callable, List, Tuple, Any


class NavigationManager:
    """
    Manages navigation between different pages of the application
    Includes sidebar rendering and current page tracking
    """
    def __init__(self):
        """Initialize the navigation manager"""
        # Dictionary to store page rendering functions
        self.pages: Dict[str, Tuple[Callable, str, int]] = {}
        
    def register_page(self, name: str, render_func: Callable, icon: str = "house", order: int = 999):
        """
        Register a page with the navigation manager
        
        Args:
            name: Display name of the page
            render_func: Function to call to render the page
            icon: Bootstrap icon name to display in navigation
            order: Order in which to display in navigation (lower numbers first)
        """
        self.pages[name] = (render_func, icon, order)
    
    def get_pages(self) -> List[Tuple[str, Callable, str]]:
        """
        Get all registered pages, sorted by order
        
        Returns:
            List of tuples containing (page_name, render_function, icon)
        """
        # Sort pages by their order value
        sorted_pages = sorted(
            [(name, func, icon) for name, (func, icon, order) in self.pages.items()],
            key=lambda x: self.pages[x[0]][2]  # Sort by order value
        )
        return sorted_pages
    
    def render_sidebar_navigation(self) -> str:
        """
        Render the navigation sidebar with icons and labels
        
        Returns:
            Name of the selected page
        """
        st.sidebar.title("Navigation")
        st.sidebar.markdown("---")
        
        # Get the current page from session state or default to Home
        current_page = st.session_state.get("current_page", "Home")
        
        # Get sorted pages
        sorted_pages = self.get_pages()
        
        # Create a radio button for each page
        selected_page = st.sidebar.radio(
            "Select Page",
            [name for name, _, _ in sorted_pages],
            format_func=lambda x: self._format_nav_item(x, sorted_pages),
            index=[name for name, _, _ in sorted_pages].index(current_page) if current_page in [name for name, _, _ in sorted_pages] else 0,
            label_visibility="collapsed"
        )
        
        st.sidebar.markdown("---")
        
        return selected_page
    
    def _format_nav_item(self, page_name: str, sorted_pages: List[Tuple[str, Callable, str]]) -> str:
        """
        Format a navigation item with an icon
        
        Args:
            page_name: Name of the page
            sorted_pages: List of sorted pages with their icons
            
        Returns:
            Formatted string with icon and page name
        """
        # Find the icon for the page, default to house icon for home page
        icon = next((icon for name, _, icon in sorted_pages if name == page_name), "home")
        return f":{icon}: {page_name}"
    
    def render_current_page(self, page_name: str) -> None:
        """
        Render the currently selected page
        
        Args:
            page_name: Name of the page to render
        """
        if page_name in self.pages:
            render_func, _, _ = self.pages[page_name]
            render_func()
        else:
            st.error(f"Page '{page_name}' not found!")


# Singleton instance of the navigation manager
_nav_manager = None


def get_nav_manager() -> NavigationManager:
    """
    Get the singleton instance of the navigation manager
    
    Returns:
        NavigationManager instance
    """
    global _nav_manager
    if _nav_manager is None:
        _nav_manager = NavigationManager()
    return _nav_manager 