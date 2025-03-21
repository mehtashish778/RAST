# -*- coding: utf-8 -*-
"""
HAZOP Analysis Tool - Home Page
"""
import streamlit as st


def render_home_page():
    """
    Render the home page of the HAZOP Analysis Tool
    """
    st.header("Welcome to HAZOP Analysis Tool")
    
    # Display application description
    st.write("""
    This application helps you conduct HAZOP (Hazard and Operability) studies 
    for process safety analysis in chemical and industrial facilities.
    """)
    
    # Create columns for features display
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Features")
        st.markdown("""
        - Chemical Database Management
        - Equipment Database Management
        - HAZOP Scenario Identification
        - LOPA (Layer of Protection Analysis)
        - Risk Assessment Matrix
        - Report Generation
        """)
    
    with col2:
        st.subheader("Getting Started")
        st.markdown("""
        1. Navigate to the Chemical Database to enter chemical properties
        2. Set up your equipment in the Equipment Database
        3. Create HAZOP scenarios using the Scenario Identification tool
        4. Perform LOPA analysis for high-risk scenarios
        5. Generate comprehensive reports
        """)
    
    # Display info box with quick tips
    st.info("""
    📌 **Quick Tip**: Use the navigation menu on the left to move between different 
    sections of the application.
    """)
    
    # Show usage statistics if available
    if 'usage_stats' in st.session_state:
        st.subheader("Recent Activity")
        st.write(st.session_state.usage_stats)


if __name__ == "__main__":
    render_home_page() 