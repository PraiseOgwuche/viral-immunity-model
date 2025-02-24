# visualization.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Try to import seaborn, but don't fail if it's not available
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    logger.info("Seaborn not found, using default matplotlib style")
    HAS_SEABORN = False

class ViralSimulationPlotter:
    """
    Handles visualization of viral infection and immune response simulation results.
    """
    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """Initialize plotter with visualization settings."""
        self.settings = settings or {
            "figsize": (10, 6),
            "dpi": 300,
            "style": "default",
            "colors": {
                "V": "#FF4B4B",  # Red for virus
                "I": "#4B4BFF",  # Blue for infected cells
                "T": "#4BFF4B",  # Green for T cells
                "A": "#FF4BFF"   # Purple for antibodies
            }
        }
        
        # Set style
        if HAS_SEABORN and self.settings["style"] == "seaborn":
            plt.style.use("seaborn")
        else:
            plt.style.use("default")
            plt.rcParams.update({
                'axes.grid': True,
                'grid.alpha': 0.3,
                'axes.labelsize': 12,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'axes.titlesize': 14
            })

    def create_figure(self) -> Tuple[Figure, plt.Axes]:
        """Create and configure a new figure."""
        fig, ax = plt.subplots(figsize=self.settings["figsize"], dpi=self.settings["dpi"])
        return fig, ax

    def plot_results(self, t: np.ndarray, results: np.ndarray, 
                    save_path: Optional[str] = None) -> Figure:
        """Create linear scale plot of simulation results."""
        fig, ax = self.create_figure()
        
        labels = ["Viral Load (V)", "Infected Cells (I)", 
                 "CD8+ T Cells (T)", "Antibodies (A)"]
        colors = list(self.settings["colors"].values())
        
        for idx, (label, color) in enumerate(zip(labels, colors)):
            ax.plot(t, results[:, idx], label=label, color=color, linewidth=2)
        
        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Population")
        ax.set_title("Viral Infection & Immune Response Dynamics")
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            self._save_figure(fig, save_path)
            
        return fig

    def plot_log_scale(self, t: np.ndarray, results: np.ndarray,
                      save_path: Optional[str] = None) -> Figure:
        """Create logarithmic scale plot of simulation results."""
        fig, ax = self.create_figure()
        
        labels = ["Viral Load (V)", "Infected Cells (I)", 
                 "CD8+ T Cells (T)", "Antibodies (A)"]
        colors = list(self.settings["colors"].values())
        
        for idx, (label, color) in enumerate(zip(labels, colors)):
            # Add small constant to avoid log(0)
            data = results[:, idx] + 1e-10
            ax.semilogy(t, data, label=label, color=color, linewidth=2)
        
        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Population (log scale)")
        ax.set_title("Viral Infection & Immune Response Dynamics (Log Scale)")
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        ax.grid(True, alpha=0.3, which="both")
        
        plt.tight_layout()
        
        if save_path:
            self._save_figure(fig, save_path)
            
        return fig

    def plot_phase_space(self, results: np.ndarray,
                        save_path: Optional[str] = None) -> Figure:
        """Create phase space plot of viral load vs immune responses."""
        fig, ax = self.create_figure()
        
        # Plot viral load vs T cells
        ax.plot(results[:, 0], results[:, 2], 
                label="V vs T cells", color=self.settings["colors"]["T"],
                linewidth=2)
        
        # Plot viral load vs Antibodies
        ax.plot(results[:, 0], results[:, 3], 
                label="V vs Antibodies", color=self.settings["colors"]["A"],
                linewidth=2)
        
        # Add small constant and set log scales
        ax.set_xscale("log")
        ax.set_yscale("log")
        
        # Customize plot
        ax.set_xlabel("Viral Load (V)")
        ax.set_ylabel("Immune Response")
        ax.set_title("Phase Space Analysis")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3, which="both")
        
        plt.tight_layout()
        
        if save_path:
            self._save_figure(fig, save_path)
            
        return fig

    def _save_figure(self, fig: Figure, save_path: str) -> None:
        """Save figure to specified path."""
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=self.settings["dpi"], bbox_inches="tight")
            logger.info(f"Figure saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save figure: {str(e)}")

# Convenience functions for direct use
def plot_results(t: np.ndarray, results: np.ndarray, 
                settings: Optional[Dict[str, Any]] = None,
                save_path: Optional[str] = None) -> Figure:
    """Convenience function to plot linear scale results."""
    plotter = ViralSimulationPlotter(settings)
    return plotter.plot_results(t, results, save_path)

def plot_log_scale(t: np.ndarray, results: np.ndarray,
                   settings: Optional[Dict[str, Any]] = None,
                   save_path: Optional[str] = None) -> Figure:
    """Convenience function to plot logarithmic scale results."""
    plotter = ViralSimulationPlotter(settings)
    return plotter.plot_log_scale(t, results, save_path)

def plot_phase_space(results: np.ndarray,
                    settings: Optional[Dict[str, Any]] = None,
                    save_path: Optional[str] = None) -> Figure:
    """Convenience function to plot phase space analysis."""
    plotter = ViralSimulationPlotter(settings)
    return plotter.plot_phase_space(results, save_path)