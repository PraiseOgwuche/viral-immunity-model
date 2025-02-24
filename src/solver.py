# solver.py

import numpy as np
from typing import Tuple, Optional
from dataclasses import asdict
from pathlib import Path
import json
import logging

from .models import ViralImmunityModel, ModelParameters
from .config import ModelConfig
from .visualization import plot_results, plot_log_scale

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimulationRunner:
    """
    Handles the execution and management of viral immunity simulations.
    """
    def __init__(self, config: ModelConfig = None):
        """
        Initialize the simulation runner with configuration.
        
        Args:
            config: ModelConfig instance with simulation parameters
        """
        self.config = config or ModelConfig()
        self.model_params = ModelParameters(**self.config.PARAMS)
        self.model = ViralImmunityModel(self.model_params)
        
    def run_simulation(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Execute the viral immunity simulation with current configuration.
        
        Returns:
            Tuple containing time points and results arrays
        """
        logger.info("Starting simulation...")
        
        # Set up time points
        t = np.linspace(
            self.config.SIMULATION_TIME["start"],
            self.config.SIMULATION_TIME["end"],
            self.config.SIMULATION_TIME["steps"]
        )
        
        # Get initial conditions
        y0 = [
            self.config.INITIAL_CONDITIONS["V"],
            self.config.INITIAL_CONDITIONS["I"],
            self.config.INITIAL_CONDITIONS["T"],
            self.config.INITIAL_CONDITIONS["A"]
        ]
        
        # Run simulation
        try:
            results = self.model.simulate(t, initial_conditions=y0)
            logger.info("Simulation completed successfully")
            return t, results
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            raise

    def save_results(self, t: np.ndarray, results: np.ndarray, 
                    output_dir: Optional[str] = "results") -> None:
        """
        Save simulation results to files.
        
        Args:
            t: Time points array
            results: Simulation results array
            output_dir: Directory to save results
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save numerical results
        np.savez(
            output_path / "simulation_results.npz",
            t=t,
            results=results,
            parameters=asdict(self.model_params)
        )
        
        # Save configuration
        with open(output_path / "config.json", "w") as f:
            json.dump(asdict(self.config), f, indent=4)
        
        logger.info(f"Results saved to {output_path}")

def run_analysis():
    """
    Main function to run simulation and generate visualizations.
    """
    # Initialize and run simulation
    runner = SimulationRunner()
    t, results = runner.run_simulation()
    
    # Save results
    runner.save_results(t, results)
    
    # Generate plots
    plot_results(t, results, settings=runner.config.PLOT_SETTINGS)
    plot_log_scale(t, results, settings=runner.config.PLOT_SETTINGS)
    
    return t, results

if __name__ == "__main__":
    run_analysis()