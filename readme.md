# HAZOP Analysis Tool

A Streamlit-based application for conducting HAZOP (Hazard and Operability) studies and LOPA (Layer of Protection Analysis) for process safety engineering.

## Overview
The HAZOP (Hazard and Operability Study) Analysis Tool is a Streamlit-based web application designed to facilitate process safety analysis in chemical and process industries. This tool combines equipment assessment, scenario analysis, Layer of Protection Analysis (LOPA), and consequence modeling in a user-friendly interface.

## Features

- Chemical Database Management
- Equipment Database Management 
- HAZOP Scenario Management and Analysis
- Consequence Modeling Functionality
- Risk Assessment Matrix
- Layer of Protection Analysis (LOPA) (Coming Soon)
- Report Generation (Coming Soon)

### Release Rate Calculations

The application includes an advanced release rate calculator with multiple modeling options:

- **Liquid Release**: Calculate release rates for liquid leaks using Bernoulli's equation with discharge coefficients
- **Gas Release**: Model both choked (sonic) and subsonic gas releases with accurate flow functions
- **Two-Phase Release**: Calculate mixed-phase releases using the homogeneous equilibrium model
- **Pipe Flow**: Model releases through pipe segments with automatic friction factor calculation
- **Flange Leaks**: Estimate leakage from flanges at different severity levels

Each calculator includes:
- Detailed input forms with guidance
- Comprehensive result display
- Interactive sensitivity analysis charts
- Integration with the chemical database for properties

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
   - Scenarios: Create and analyze HAZOP scenarios

## Testing

The project includes a comprehensive test suite with pytest:

1. Install test dependencies:
   ```
   pip install -r tests/requirements-test.txt
   ```

2. Run all tests with coverage reporting:
   ```
   python -m pytest --cov=app
   ```

3. View test results and coverage reports in the terminal or generate HTML reports:
   ```
   python -m pytest --cov=app --cov-report=html
   ```

See the [tests/README.md](tests/README.md) file for more detailed testing instructions.

### Test Coverage

Current test coverage is at ~35% of the codebase, with excellent coverage in:
- Release rate calculation module (99% coverage)
- Consequence calculation module (88% coverage)
- Data access layer (53% coverage)
- Database management (45% coverage)

Key tested components:
- Release rate calculations for liquid, gas, and two-phase flows
- Pipe and flange leak rate calculations
- Consequence risk scoring and categorization
- Database connection and query execution
- Data access objects for equipment and scenarios
- Basic application functionality

Ongoing test development is focused on increasing coverage for UI components and remaining core modules.

## Release Rate Calculations

The application implements comprehensive release rate calculations for various fluid scenarios, following industry-standard approaches and equations:

### Liquid Release Rate

For liquid release through a hole or orifice, the application uses Bernoulli's equation with a discharge coefficient:

```
velocity = Cd * √(2 * ΔP / ρ)
mass_flow_rate = A * velocity * ρ
```

Where:
- Cd = Discharge coefficient (dimensionless)
- ΔP = Pressure differential (Pa)
- ρ = Fluid density (kg/m³)
- A = Hole area (m²)

### Gas Release Rate

For gas release, the application handles both choked (sonic) and subsonic flow conditions:

1. **Choked Flow** (when P₂/P₁ ≤ Critical Pressure Ratio):
   ```
   critical_pressure_ratio = (2/(k+1))^(k/(k-1))
   flow_function = √(k * (2/(k+1))^((k+1)/(k-1)))
   mass_flow_rate = Cd * A * P₁ * flow_function * √(MW/(R*T))
   ```

2. **Subsonic Flow** (when P₂/P₁ > Critical Pressure Ratio):
   ```
   flow_parameter = √((2*k)/(k-1)) * √(pressure_ratio^(2/k) * (1-pressure_ratio^((k-1)/k)))
   mass_flow_rate = Cd * A * flow_parameter * P₁ * √(ρ/P₁)
   ```

Where:
- Cd = Discharge coefficient
- A = Hole area (m²)
- P₁ = Upstream pressure (Pa)
- P₂ = Downstream pressure (Pa)
- k = Specific heat ratio (Cp/Cv)
- MW = Molecular weight (kg/mol)
- R = Universal gas constant (J/(mol·K))
- T = Temperature (K)
- pressure_ratio = P₂/P₁
- ρ = Gas density (kg/m³)

### Two-Phase Release Rate

For two-phase release, the application uses a homogeneous equilibrium model:

```
mixture_density = 1/((liquid_fraction/liquid_density) + ((1-liquid_fraction)/vapor_density))
velocity = Cd * √(2 * ΔP / mixture_density)
mass_flow_rate = A * velocity * mixture_density
```

Where:
- mixture_density = Effective density of the two-phase mixture (kg/m³)
- liquid_fraction = Mass fraction of liquid in the mixture (0-1)
- liquid_density = Density of the liquid phase (kg/m³)
- vapor_density = Density of the vapor phase (kg/m³)

### Pipe Release Rate

For release through a pipe segment, the application uses the Darcy-Weisbach equation:

```
velocity = √(2 * ΔP / (ρ * (1 + 4 * f * L/D)))
mass_flow_rate = A * velocity * ρ
```

Where:
- f = Friction factor (calculated using the Colebrook equation or user-specified)
- L = Pipe length (m)
- D = Pipe diameter (m)

### Discharge Coefficient

The discharge coefficient varies with Reynolds number and orifice type:

1. **Sharp Orifice**:
   - Re < 10: Cd = 0.5
   - 10 ≤ Re < 1000: Cd = 0.5 + 0.11 * (log₁₀(Re) - 1) / 2
   - Re ≥ 1000: Cd = 0.61

2. **Rounded Orifice**: Cd = 0.98

3. **Pipe Entrance**: Cd = 0.82

### Flange Leak Rate

For flange leaks, the application calculates the leak area based on flange size and leak type:

```
leak_area = flange_circumference * leak_gap
velocity = Cd * √(2 * P / ρ)
mass_flow_rate = leak_area * velocity * ρ
```

Where:
- leak_gap = Gap size based on leak type (small: 0.025 mm, medium: 0.25 mm, large: 2.5 mm)
- flange_circumference = π * flange_diameter

## Additional Calculation Models

### Consequence Modeling

#### Pool Fire Modeling
For pool fires resulting from liquid releases, the application calculates:

```
pool_area = liquid_release_rate * evaporation_time / (density * pool_depth)
pool_diameter = 2 * √(pool_area / π)
flame_height = 42 * pool_diameter * (mass_burning_rate / (ρ_air * √(g * pool_diameter)))^0.61
thermal_radiation = τ_a * E * view_factor
```

Where:
- evaporation_time = Time for the pool to reach equilibrium (s)
- pool_depth = Standard pool depth (typically 0.01 m for continuous spills)
- mass_burning_rate = Burning rate of the liquid (kg/m²s)
- τ_a = Atmospheric transmissivity
- E = Surface emissive power (kW/m²)
- view_factor = Geometric view factor based on distance and orientation

#### Vapor Cloud Dispersion
For vapor dispersion, the application uses the Gaussian dispersion model:

```
C(x,y,z) = (Q / (2π * u * σy * σz)) * exp(-y² / (2σy²)) * [exp(-(z-h)² / (2σz²)) + exp(-(z+h)² / (2σz²))]
```

Where:
- C = Concentration at point (x,y,z) (kg/m³)
- Q = Release rate (kg/s)
- u = Wind speed (m/s)
- σy, σz = Dispersion coefficients (m)
- h = Release height (m)

### Risk Assessment

#### Risk Score Calculation
The application calculates risk scores using:

```
risk_score = likelihood_score * consequence_score
```

Where:
- likelihood_score = Numerical value from 1-5 representing probability
- consequence_score = Numerical value from 1-5 representing severity

#### Likelihood Estimation
For equipment failure likelihood:

```
failure_frequency = base_failure_rate * service_factor * environment_factor * maintenance_factor
```

Where:
- base_failure_rate = Industry standard failure rate for the equipment type
- service_factor = Adjustment based on service conditions
- environment_factor = Adjustment based on environmental conditions
- maintenance_factor = Adjustment based on maintenance quality

#### LOPA Risk Reduction
For LOPA (Layer of Protection Analysis) calculations:

```
mitigated_frequency = initiating_event_frequency * PFD₁ * PFD₂ * ... * PFDₙ
risk_reduction_factor = initiating_event_frequency / mitigated_frequency
```

Where:
- PFD = Probability of Failure on Demand for each protection layer
- initiating_event_frequency = Frequency of the initiating event (per year)

## Data Management

- The application uses SQLite for data storage by default
- Database files are stored in the `app/data` directory
- Data can be imported/exported from Excel or CSV files

## Requirements

- Python 3.8 or newer
- Streamlit 1.22.0 or newer
- See requirements.txt for complete list of dependencies

## Running the Application

1. Ensure you have all dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Run the application from the project root:
   ```
   python -m streamlit run app/app.py
   ```

3. The application will be available at `http://localhost:8501` in your web browser.

## Application Structure

The application follows a modular architecture:

```
hazop-analysis-tool/
├── app/                # Main application code
│   ├── core/           # Core calculation modules
│   │   ├── consequence.py    # Consequence modeling
│   │   ├── release.py        # Release rate calculations
│   │   ├── chemical_model.py # Chemical data models
│   │   └── equipment_model.py # Equipment models
│   ├── pages/          # Streamlit UI pages
│   │   ├── home.py           # Home page
│   │   ├── chemicals.py      # Chemical database UI
│   │   ├── equipment.py      # Equipment database UI
│   │   ├── scenarios.py      # Scenario management UI
│   │   └── release.py        # Release calculator UI
│   ├── utils/          # Utility functions
│   │   ├── database.py       # Database management
│   │   ├── data_access.py    # Data access objects
│   │   └── navigation.py     # Navigation management
│   └── app.py          # Main application entry point
├── tests/              # Test suite
├── resources/          # Excel tools and other resources
└── requirements.txt    # Application dependencies
```

## Debugging Tips

If you encounter import errors when running the application:

1. Make sure all directories have appropriate `__init__.py` files
2. Check for circular imports (modules importing each other)
3. Use relative imports within the same package
4. When modifying parameters in method calls, ensure parameter names match exactly

Common fixes:
- Convert `from app.core.module import ...` to `from core.module import ...` when inside the app package
- Import modules where needed rather than at the top-level to avoid circular dependencies
- Ensure the working directory is set correctly when running the application

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

### Phase 2: Scenario Management Tools ✅ (Completed)
4. **Scenario Identification Module** ✅
   - Create scenario template structures
   - Implement basic scenario generation logic
   - Build Streamlit interface for scenario browsing/editing

5. **Scenario Analysis** ✅
   - Implement the scenario listing functionality
   - Create filtering and sorting capabilities
   - Develop visualization of scenario relationships
   - Add risk matrix visualization

6. **Basic Consequence Analysis** ✅
   - Implement consequence calculation algorithms
   - Create visualization for consequence magnitudes
   - Build parameter sensitivity analysis tools

### Phase 3: Risk Analysis Tools ✅ (Completed)
7. **Release Rate Calculations** ✅
   - Implemented liquid/gas/two-phase release models
   - Created discharge coefficient calculations
   - Implemented Reynolds number calculation
   - Added pipe release and flange leak calculations
   - Comprehensive test suite with 99% code coverage
   - Fixed calculation accuracy for gas release rates
   - Created interactive UI for release calculations with sensitivity analysis
   - Fixed circular import issues and parameter naming in release module

8. **Risk Assessment** ✅
   - Implement risk ranking methodology
   - Create interactive risk matrix visualization
   - Develop scenario classification tools
   - Unit tests for risk scoring functionality (88% coverage)

9. **Testing Infrastructure** ✅
   - Create comprehensive test suite for core functionality
   - Implement mocks for database and external dependencies
   - Setup continuous testing workflow
   - Tests for release calculator, consequence calculator, database, and data access layers
   - Fixed import path issues for proper test execution

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

19. **Test Coverage Enhancement**
    - Expand unit test coverage to UI components
    - Implement integration tests for end-to-end workflows
    - Create automated performance testing

## Project Structure
```
hazop-analysis-tool/
├── app/                # Main application code
│   ├── core/           # Core business logic
│   ├── data/           # Data storage
│   ├── pages/          # Streamlit page modules
│   ├── utils/          # Utility functions
│   └── app.py          # Main application entry point
├── tests/              # Test suite
│   ├── test_*.py       # Test modules
│   └── conftest.py     # Test fixtures and configuration
├── resources/          # Static resources
├── requirements.txt    # Application dependencies
└── README.md           # Project documentation
```
