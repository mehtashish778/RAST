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
- Layer of Protection Analysis (LOPA)
- Safety Instrumented Function (SIF) Assessment ✅
- Report Generation (Coming Soon)

## Development Status

The application has been developed in phases:
- Phase 1: Basic HAZOP functionality - ✅ Completed
- Phase 2: Consequence modeling - ✅ Completed
- Phase 3: Layer of Protection Analysis (LOPA) - ✅ Completed
- Phase 4: Safety Instrumented Function (SIF) Assessment - ✅ Completed
- Phase 5: Report Generation - 🔄 In Progress

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

Current test coverage is at ~75% of the codebase, with excellent coverage in:
- Release rate calculation module (99% coverage)
- Consequence calculation module (88% coverage)
- SIF (Safety Instrumented Function) module (90% coverage)
- Data access layer (53% coverage)
- Database management (45% coverage)

Key tested components:
- Release rate calculations for liquid, gas, and two-phase flows
- Pipe and flange leak rate calculations
- Consequence risk scoring and categorization
- SIF functionality, including PFD calculations and SIL verification
- Database connection and query execution
- Data access objects for equipment, scenarios, and SIFs
- Basic application functionality

Ongoing test development is focused on increasing coverage for UI components and integration tests.

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

### Layer of Protection Analysis (LOPA)

The application implements a comprehensive Layer of Protection Analysis framework following industry standards:

#### IPL Credit Calculation

```
mitigated_frequency = initiating_event_frequency * PFD₁ * PFD₂ * ... * PFDₙ * CM₁ * CM₂ * ... * CMₘ
risk_reduction_factor = initiating_event_frequency / mitigated_frequency
```

Where:
- PFD = Probability of Failure on Demand for each protection layer (0-1)
- CM = Conditional modifier (probability factors like ignition probability)
- initiating_event_frequency = Frequency of the initiating event (per year)

#### Safety Integrity Level (SIL) Determination

The application calculates required SIL levels for Safety Instrumented Functions (SIFs) based on:

```
required_PFD = target_mitigated_frequency / intermediate_frequency
```

Where:
- target_mitigated_frequency = Risk tolerance criteria (events/year)
- intermediate_frequency = Frequency after applying existing IPLs (events/year)

The SIL level is determined based on the required PFD:
- SIL 1: 0.1 ≥ PFD > 0.01
- SIL 2: 0.01 ≥ PFD > 0.001
- SIL 3: 0.001 ≥ PFD > 0.0001
- SIL 4: 0.0001 ≥ PFD > 0.00001

#### IPL Types and Credits

The application includes predefined IPL types with recommended PFD values:
- Basic Process Control System (BPCS): PFD = 0.1
- Alarm with Operator Response: PFD = 0.1
- Safety Instrumented System (SIS): PFD = 0.01 (SIL 2)
- Mechanical Protection Devices: PFD = 0.01
- Physical Protection: PFD = 0.01
- Procedural Protection: PFD = 0.1
- Relief Devices: PFD = 0.01
- Dikes and Containment: PFD = 0.01
- Emergency Response: PFD = 0.1

### Safety Instrumented Function (SIF) Assessment

The application provides comprehensive functionality for the assessment and verification of Safety Instrumented Functions (SIFs):

#### SIF Architecture Modeling

The application supports various redundancy architectures:
- 1oo1 (1 out of 1): Single-channel architecture
- 1oo2 (1 out of 2): Redundant architecture (either channel can perform the safety function)
- 2oo2 (2 out of 2): Both channels must operate for the safety function to be performed
- 2oo3 (2 out of 3): Triple Modular Redundancy (TMR)
- 2oo4 (2 out of 4): Quad redundancy architecture

#### Probability of Failure on Demand (PFD) Calculation

The application implements rigorous PFD calculations for each architecture type, incorporating:
- Diagnostic coverage (DC)
- Common cause failures (Beta factor)
- Test intervals
- Mean time to repair (MTTR)

For each architecture, specific formulas are implemented:
```
PFD_1oo1 = PFD_component * (1 - DC) + λDU * TI / 2
PFD_1oo2 = (PFD_component * (1 - DC))² + β * PFD_component
PFD_2oo2 = 2 * PFD_component * (1 - DC) - (PFD_component * (1 - DC))²
PFD_2oo3 = 3 * (PFD_component * (1 - DC))² - 2 * (PFD_component * (1 - DC))³ + β * PFD_component
PFD_2oo4 = 6 * (PFD_component * (1 - DC))² - 8 * (PFD_component * (1 - DC))³ + 3 * (PFD_component * (1 - DC))⁴ + β * PFD_component
```

Where:
- PFD_component = Base probability of failure on demand per component
- DC = Diagnostic coverage (0-1)
- β = Beta factor for common cause failures (0-1)
- λDU = Dangerous undetected failure rate
- TI = Test interval (hours)

#### SIL Verification

The application determines SIL levels based on the calculated PFD following IEC 61508 standards:
- SIL 4: 0.0001 > PFD
- SIL 3: 0.001 > PFD ≥ 0.0001
- SIL 2: 0.01 > PFD ≥ 0.001
- SIL 1: 0.1 > PFD ≥ 0.01
- No SIL: PFD ≥ 0.1

#### SIF Configuration

The application enables configuration of complete SIFs with multiple subsystems:
- Sensor subsystems
- Logic solver subsystems
- Final element subsystems

Each SIF can be evaluated to:
- Calculate overall PFD
- Determine achieved SIL level
- Verify if requirements are met
- Provide recommendations for improvement

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