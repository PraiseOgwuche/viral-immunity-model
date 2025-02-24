# models.py

import numpy as np
from scipy.integrate import odeint
from typing import List, Dict, Optional, Tuple

class ViralImmunityModel:
    """
    Viral infection and immune response model.
    Implements system of ODEs describing viral dynamics and immune response.
    """
    def __init__(self, params: Dict[str, float]):
        """
        Initialize model with parameters from config.
        
        Args:
            params: Dictionary of model parameters
        """
        self.params = params

    def odes(self, state: List[float], t: float, params: Dict[str, float]) -> List[float]:
        """
        System of ODEs describing viral-immune dynamics.
        
        Args:
            state: Current state vector [V, I, T, A]
            t: Current time point
            params: Model parameters
            
        Returns:
            List of derivatives [dV/dt, dI/dt, dT/dt, dA/dt]
        """
        V, I, T, A = state  # Unpack state variables

        # Calculate immune system activation (smooth transition)
        immune_scaling = 1 / (1 + np.exp(-3 * (t - params["tau"])))

        # Viral dynamics
        dVdt = (params["p"] * I                     # Viral production
                - params["c"] * V                   # Natural clearance
                - params["k_a"] * A * V             # Antibody neutralization
                - 0.005 * T * V)                    # Direct T cell effect

        # Infected cell dynamics
        dIdt = (params["beta"] * V * (1 - I/1e3)   # Cell infection with carrying capacity
                - params["delta"] * I               # Natural cell death
                - params["k_t"] * T * I)            # T cell killing

        # T cell dynamics
        dTdt = (immune_scaling * params["r"] * T * I / (params["theta"] + I)  # Proliferation
                + params["s_t"] * I * T / (100 + I)  # Additional stimulation
                - params["d_t"] * T)                 # Natural death

        # Antibody dynamics
        dAdt = (immune_scaling * params["s_a"] * V * T / (100 + V)  # Production
                + immune_scaling * 0.1 * I           # Additional stimulation from infected cells
                - params["d_a"] * A)                 # Natural decay

        return [dVdt, dIdt, dTdt, dAdt]

    def simulate(self, 
                t: np.ndarray, 
                initial_conditions: Optional[List[float]] = None) -> np.ndarray:
        """
        Simulate the viral-immune dynamics.
        
        Args:
            t: Array of time points to simulate
            initial_conditions: Initial values for [V, I, T, A]
            
        Returns:
            Array of simulation results with shape (len(t), 4)
        """
        if initial_conditions is None:
            raise ValueError("Initial conditions must be provided")

        # Run simulation
        result = odeint(
            func=self.odes,
            y0=initial_conditions,
            t=t,
            args=(self.params,),
            rtol=1e-6,       # Relative tolerance for solver
            atol=1e-6,       # Absolute tolerance for solver
            full_output=False
        )

        # Ensure non-negative values
        return np.maximum(result, 0)

    def get_derived_quantities(self, 
                             t: np.ndarray, 
                             results: np.ndarray) -> Dict[str, float]:
        """
        Calculate derived quantities from simulation results.
        
        Args:
            t: Time points array
            results: Simulation results array
            
        Returns:
            Dictionary of derived quantities
        """
        V = results[:, 0]  # Viral load
        T = results[:, 2]  # T cells
        A = results[:, 3]  # Antibodies

        # Calculate key metrics
        peak_viral_load = np.max(V)
        peak_viral_time = t[np.argmax(V)]
        
        # Find clearance time (when viral load drops below 1% of peak)
        threshold = peak_viral_load * 0.01
        clearance_idx = np.where(V < threshold)[0]
        clearance_time = t[clearance_idx[0]] if len(clearance_idx) > 0 else np.inf

        return {
            "peak_viral_load": peak_viral_load,
            "peak_viral_time": peak_viral_time,
            "clearance_time": clearance_time,
            "max_t_cells": np.max(T),
            "peak_antibodies": np.max(A)
        }

    def check_stability(self, results: np.ndarray) -> bool:
        """
        Check if simulation results are stable.
        
        Args:
            results: Simulation results array
            
        Returns:
            True if results are stable, False otherwise
        """
        # Check for infinities or NaN
        if np.any(~np.isfinite(results)):
            return False

        # Check for unrealistic values
        max_values = {
            "V": 1e8,  # Maximum reasonable viral load
            "I": 1e6,  # Maximum reasonable infected cells
            "T": 1e5,  # Maximum reasonable T cells
            "A": 1e4   # Maximum reasonable antibodies
        }

        for i, max_val in enumerate(max_values.values()):
            if np.any(results[:, i] > max_val):
                return False

        return True