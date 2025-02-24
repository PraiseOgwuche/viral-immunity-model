# viral-immunity-model# Viral Infection & Immune Response Simulation

A web-based simulation tool for modeling viral infection dynamics and immune system responses. This application provides an interactive interface to explore how viruses spread and how the immune system responds through T cells and antibodies.

## Overview

This simulation models the interaction between:
- Viral load (V)
- Infected cells (I)
- CD8+ T cells (T)
- Antibodies (A)

The model captures key biological processes including:
- Viral replication and spread
- Immune system activation and response
- T cell-mediated killing of infected cells
- Antibody neutralization of free virus

## Features

- Real-time simulation visualization
- Interactive parameter adjustment
- Multiple visualization options (linear/log scale)
- Downloadable simulation results
- Biologically relevant parameter ranges
- Key metrics calculation (peak viral load, clearance time, etc.)

## Project Structure

```
viral-immunity-model/
├── src/
│   ├── api.py          # FastAPI backend implementation
│   ├── config.py       # Model configuration and parameters
│   ├── models.py       # Core mathematical model
│   ├── solver.py       # Numerical solver implementation
│   └── visualization.py # Plotting and visualization
├── frontend/
│   └── static/
│       ├── index.html  # Web interface
│       ├── script.js   # Frontend logic
│       └── style.css   # Styling
├── requirements.txt    # Python dependencies
└── README.md          # Documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/viral-immunity-model.git
cd viral-immunity-model
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the server:
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Model Parameters

### Viral Dynamics
- β (beta): Infection rate (virion^-1 day^-1)
- δ (delta): Infected cell death rate (day^-1)
- p: Viral production rate (virion cell^-1 day^-1)
- c: Viral clearance rate (day^-1)

### Immune Response
- k_t: T cell killing rate (cell^-1 day^-1)
- k_a: Antibody neutralization rate (molecule^-1 day^-1)
- r: T cell proliferation rate (day^-1)
- θ (theta): Half-saturation constant (cells)

### Response Timing
- τ (tau): Delay in adaptive response (days)
- s_t: T cell stimulation rate
- s_a: Antibody stimulation rate

## Mathematical Model

The system is described by four coupled ordinary differential equations:

1. Viral dynamics:
```
dV/dt = p*I - c*V - k_a*A*V
```

2. Infected cell dynamics:
```
dI/dt = β*V*(1-I/K) - δ*I - k_t*T*I
```

3. T cell dynamics:
```
dT/dt = r*T*I/(θ+I) + s_t*I*T/(100+I) - d_t*T
```

4. Antibody dynamics:
```
dA/dt = s_a*V*T/(100+V) + 0.1*I - d_a*A
```

## References

1. Perelson & Ke (2021) Nature Reviews Immunology
2. Cao et al. (2020) Nature Medicine
3. Tan et al. (2021) Immunity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Your Name
- Contributors

## Acknowledgments

- References to any research papers or resources used
- Thanks to contributors and reviewers