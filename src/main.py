# main.py

import typer
from pathlib import Path
import logging
from typing import Optional

from .solver import SimulationRunner
from .config import ModelConfig
from .visualization import ViralSimulationPlotter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Typer app
app = typer.Typer(help="Viral Infection & Immune Response Simulation CLI")

@app.command()
def run_simulation(
    duration: Optional[float] = typer.Option(None, help="Simulation duration in days"),
    output_dir: str = typer.Option("results", help="Directory to save results"),
    plot_types: list[str] = typer.Option(
        ["linear", "log", "phase"],
        help="Types of plots to generate"
    )
):
    """
    Run viral infection simulation and generate visualizations.
    """
    try:
        logger.info("Initializing simulation...")
        
        # Set up components
        config = ModelConfig()
        if duration is not None:
            config.SIMULATION_TIME["end"] = duration
        
        runner = SimulationRunner(config)
        plotter = ViralSimulationPlotter()
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Run simulation
        logger.info("Running simulation...")
        t, results = runner.run_simulation()
        
        # Save numerical results
        logger.info("Saving results...")
        runner.save_results(t, results, output_dir=output_dir)
        
        # Generate and save plots
        logger.info("Generating plots...")
        for plot_type in plot_types:
            plot_path = output_path / f"{plot_type}_plot.png"
            if plot_type == "linear":
                fig = plotter.plot_results(t, results)
            elif plot_type == "log":
                fig = plotter.plot_log_scale(t, results)
            elif plot_type == "phase":
                fig = plotter.plot_phase_space(results)
            else:
                logger.warning(f"Unknown plot type: {plot_type}")
                continue
            
            fig.savefig(plot_path)
            logger.info(f"Saved {plot_type} plot to {plot_path}")
        
        logger.info("Simulation completed successfully")
        
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        raise typer.Exit(1)

def main():
    """Entry point for the application."""
    app()

if __name__ == "__main__":
    main()