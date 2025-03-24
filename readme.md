# HAZOP Analysis Tool

A Streamlit-based application for conducting HAZOP (Hazard and Operability) studies and LOPA (Layer of Protection Analysis) for process safety engineering.

## Overview
The HAZOP (Hazard and Operability Study) Analysis Tool is a Streamlit-based web application designed to facilitate process safety analysis in chemical and process industries. This tool combines equipment assessment, scenario analysis, Layer of Protection Analysis (LOPA), and consequence modeling in a user-friendly interface.

## Features

- Chemical Database Management
- Equipment Database Management 
- HAZOP Scenario Identification (Coming Soon)
- LOPA Worksheet (Coming Soon)
- Report Generation (Coming Soon)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/mehtashish778/hazop-analysis-tool.git
   cd hazop-analysis-tool
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   streamlit run app/app.py
   ```

2. Navigate to `http://localhost:8501` in your web browser.

3. Use the sidebar navigation to switch between different tools:
   - Home: Overview of the application
   - Chemical Database: Manage chemical properties
   - Equipment Database: Manage process equipment
   - (More features coming soon)

## Data Management

- The application uses SQLite for data storage by default
- Database files are stored in the `app/data` directory
- Data can be imported/exported from Excel or CSV files

## Requirements

- Python 3.8 or newer
- Streamlit 1.22.0 or newer
- See requirements.txt for complete list of dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Implementation Plan

### Phase 1: Core Data Models and Basic UI ✅ (Completed)
1. **Project Setup and Initial Streamlit App** ✅
   - Set up project structure
   - Create basic Streamlit UI skeleton
   - Implement navigation system between different tools

2. **Chemical Data Module** ✅
   - Create data models for chemicals
   - Implement import/export of chemical properties
   - Develop Streamlit interface for chemical data viewing/editing

3. **Equipment Data Module** ✅
   - Define equipment class structure
   - Create equipment data entry forms in Streamlit
   - Implement equipment data storage and retrieval

### Phase 2: Scenario Management Tools 🚧 (Not Started)
4. **Scenario Identification Module**
   - Create scenario template structures
   - Implement basic scenario generation logic
   - Build Streamlit interface for scenario browsing/editing

5. **Scenario List Generator**
   - Implement the scenario listing functionality
   - Create filtering and sorting capabilities
   - Develop visualization of scenario relationships

6. **Basic Consequence Analysis**
   - Implement simple consequence calculation algorithms
   - Create visualization for consequence magnitudes
   - Build parameter sensitivity analysis tools

### Phase 3: Risk Analysis Tools
7. **Flash Calculation Module**
   - Implement core thermodynamic calculations
   - Create material property correlations
   - Develop visualization of calculation results

8. **Release Rate Calculations**
   - Implement liquid/gas release models
   - Create discharge coefficient calculations
   - Build Streamlit interface for release scenario definition

9. **Risk Assessment Matrix**
   - Implement risk ranking methodology
   - Create interactive risk matrix visualization
   - Develop scenario classification tools

### Phase 4: LOPA Implementation
10. **Independent Protection Layer (IPL) Module**
    - Create IPL definition and management interface
    - Implement IPL credit calculations
    - Develop IPL visualization and documentation tools

11. **LOPA Worksheet Implementation**
    - Build scenario-specific LOPA analysis interface
    - Implement risk reduction calculations
    - Create LOPA results visualization

12. **SIF Assessment Tools**
    - Implement SIF definition and evaluation
    - Create SIF verification calculations
    - Develop SIF documentation generators

### Phase 5: Integration and Advanced Features
13. **Results Dashboard**
    - Create comprehensive results view
    - Implement dynamic filtering and exploration
    - Develop custom report generation

14. **Data Import/Export System**
    - Implement Excel import/export capability
    - Create project file management system
    - Build data merging functionality

15. **Quality Assessment Tools**
    - Implement input validation checks
    - Create consistency verification tools
    - Develop quality metric visualization

### Phase 6: Enhancements and Optimization
16. **Batch Processing Tools**
    - Implement batch calculation capabilities
    - Create progress tracking and error handling
    - Develop comparison tools for multiple scenarios

17. **Advanced Visualization**
    - Implement interactive charts and graphs
    - Create equipment/scenario relationship maps
    - Develop 3D visualization of consequences (if applicable)

18. **Performance Optimization**
    - Improve calculation speed for complex operations
    - Implement caching strategies
    - Optimize database queries and data handling

## Project Structure
