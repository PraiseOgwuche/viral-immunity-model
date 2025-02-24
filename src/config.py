# config.py

from dataclasses import dataclass, field
from typing import Dict, Any

def get_default_params() -> Dict[str, float]:
    """
    Final tuned parameters based on viral infection literature.
    """
    return {
        # Viral dynamics (keep similar as working well)
        "beta": 1.0e-5,     # Infection rate (virion^-1 day^-1)
        "delta": 0.3,       # Infected cell death rate (day^-1)
        "p": 40.0,          # Viral production rate (virion cell^-1 day^-1)
        "c": 0.1,           # Viral clearance rate (day^-1)
        
        # Immune response (strengthen and adjust timing)
        "k_t": 2.0e-4,      # Increased T cell killing rate
        "k_a": 2.0e-3,      # Increased antibody neutralization rate
        "r": 2.5,           # Higher T cell proliferation
        "theta": 50.0,      # Lower half-saturation for faster response
        
        # Decay rates (slower for more sustained response)
        "d_t": 0.02,        # Slower T cell decay
        "d_a": 0.01,        # Slower antibody decay
        
        # Response timing (adjust for better coordination)
        "tau": 2.0,         # Earlier immune response
        "s_t": 1.5,         # Stronger T cell stimulation
        "s_a": 0.8          # Stronger antibody stimulation
    }

def get_default_initial_conditions() -> Dict[str, float]:
    """Initial conditions for the model variables."""
    return {
        "V": 10.0,      # Initial viral load
        "I": 1.0,       # Initial infected cells
        "T": 20.0,      # Lower initial T cells
        "A": 0.0        # No initial antibodies
    }
def get_default_simulation_time() -> Dict[str, Any]:
    """Simulation time settings."""
    return {
        "start": 0,      # Start time (days)
        "end": 30,       # Duration (days)
        "steps": 1000    # Number of time points
    }

def get_default_plot_settings() -> Dict[str, Any]:
    """Plot configuration settings."""
    return {
        "figsize": (10, 6),
        "dpi": 300,
        "style": "default",
        "colors": {
            "V": "#FF4B4B",  # Red for virus
            "I": "#4B4BFF",  # Blue for infected cells
            "T": "#4BFF4B",  # Green for T cells
            "A": "#FF4BFF"   # Purple for antibodies
        },
        "y_max": {
            "V": 1e6,    # Maximum viral load to display
            "I": 1e5,    # Maximum infected cells to display
            "T": 1e4,    # Maximum T cells to display
            "A": 1e3     # Maximum antibody level to display
        },
        "labels": {
            "V": "Viral Load (V)",
            "I": "Infected Cells (I)",
            "T": "CD8+ T Cells (T)",
            "A": "Antibodies (A)"
        }
    }

@dataclass
class ModelConfig:
    """
    Configuration class for viral immunity model parameters and settings.
    All parameters are sourced from peer-reviewed literature with biologically
    relevant units and constraints.
    """
    PARAMS: Dict[str, float] = field(default_factory=get_default_params)
    INITIAL_CONDITIONS: Dict[str, float] = field(default_factory=get_default_initial_conditions)
    SIMULATION_TIME: Dict[str, Any] = field(default_factory=get_default_simulation_time)
    PLOT_SETTINGS: Dict[str, Any] = field(default_factory=get_default_plot_settings)

    def validate_parameters(self):
        """
        Ensure parameters are within biologically realistic ranges.
        Raises ValueError if any parameter is outside its valid range.
        """
        constraints = {
            # Viral dynamics constraints
            "beta": (1e-8, 1e-4),      # Infection rate bounds
            "delta": (0.1, 2.0),       # Cell death rate bounds
            "p": (1.0, 1000.0),        # Viral production bounds
            "c": (0.01, 10.0),         # Viral clearance bounds
            
            # Immune response constraints
            "k_t": (1e-7, 1e-3),       # T cell killing bounds
            "k_a": (1e-6, 1e-2),       # Antibody neutralization bounds
            "r": (0.1, 5.0),           # T cell proliferation bounds
            "theta": (1e1, 1e4),       # Half-saturation bounds
            
            # Decay rate constraints
            "d_t": (0.01, 1.0),        # T cell death bounds
            "d_a": (0.01, 0.5),        # Antibody decay bounds
            
            # Response timing constraints
            "tau": (0.1, 10.0),        # Delay bounds
            "s_t": (0.1, 2.0),         # T cell stimulation bounds
            "s_a": (0.1, 1.0)          # Antibody stimulation bounds
        }
        
        for param, (min_val, max_val) in constraints.items():
            if param in self.PARAMS:
                if not min_val <= self.PARAMS[param] <= max_val:
                    raise ValueError(
                        f"Parameter {param} = {self.PARAMS[param]} outside valid range "
                        f"[{min_val}, {max_val}]"
                    )

    def validate_initial_conditions(self):
        """
        Ensure initial conditions are non-negative and within reasonable ranges.
        """
        constraints = {
            "V": (0.0, 1e6),    # Viral load bounds
            "I": (0.0, 1e5),    # Infected cell bounds
            "T": (0.0, 1e4),    # T cell bounds
            "A": (0.0, 1e3)     # Antibody bounds
        }
        
        for var, (min_val, max_val) in constraints.items():
            if not min_val <= self.INITIAL_CONDITIONS[var] <= max_val:
                raise ValueError(
                    f"Initial condition {var} = {self.INITIAL_CONDITIONS[var]} "
                    f"outside valid range [{min_val}, {max_val}]"
                )

# Create default configuration
default_config = ModelConfig()

# Validate default configuration
default_config.validate_parameters()
default_config.validate_initial_conditions()