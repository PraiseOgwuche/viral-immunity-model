# api.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import io
import tempfile
import base64
from typing import Dict, Any, Optional

from .models import ViralImmunityModel
from .config import ModelConfig
from .visualization import ViralSimulationPlotter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Viral Infection & Immune Response API",
    description="API for running viral infection simulations and generating visualizations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
config = ModelConfig()
model = ViralImmunityModel(config.PARAMS)
plotter = ViralSimulationPlotter()

# Mount static files
static_path = Path("frontend/static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML page."""
    try:
        frontend_path = static_path / "index.html"
        if not frontend_path.exists():
            raise FileNotFoundError
        return FileResponse(str(frontend_path))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend file not found")

@app.get("/api/run-simulation")
async def run_simulation_api(
    duration: Optional[float] = None,
    plot_type: str = "linear",
    beta: Optional[float] = None,
    delta: Optional[float] = None,
    k_t: Optional[float] = None,
    k_a: Optional[float] = None
) -> Dict[str, Any]:
    """Run viral infection simulation with optional parameters."""
    try:
        # Create simulation parameters
        params = config.PARAMS.copy()
        
        # Update parameters if provided
        if beta is not None:
            params["beta"] = beta
        if delta is not None:
            params["delta"] = delta
        if k_t is not None:
            params["k_t"] = k_t
        if k_a is not None:
            params["k_a"] = k_a

        # Create time points
        t_end = duration if duration is not None else config.SIMULATION_TIME["end"]
        t = np.linspace(0, t_end, config.SIMULATION_TIME["steps"])
        
        # Run simulation with updated parameters
        model = ViralImmunityModel(params)
        results = model.simulate(t, list(config.INITIAL_CONDITIONS.values()))
        
        # Get derived quantities
        metrics = model.get_derived_quantities(t, results)
        
        # Check simulation stability
        if not model.check_stability(results):
            raise ValueError("Simulation produced unstable results")
        
        # Prepare response
        response_data = {
            "success": True,
            "data": {
                "time": t.tolist(),
                "viral_load": results[:, 0].tolist(),
                "infected_cells": results[:, 1].tolist(),
                "t_cells": results[:, 2].tolist(),
                "antibodies": results[:, 3].tolist()
            },
            "metrics": {
                "peak_viral_load": float(metrics["peak_viral_load"]),
                "clearance_time": float(metrics["clearance_time"]),
                "max_t_cells": float(metrics["max_t_cells"]),
                "peak_antibodies": float(metrics["peak_antibodies"])
            }
        }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/plot/{plot_type}")
async def get_plot(plot_type: str):
    """Generate and return a specific type of plot."""
    try:
        # Create time points
        t = np.linspace(0, config.SIMULATION_TIME["end"], config.SIMULATION_TIME["steps"])
        
        # Run simulation
        results = model.simulate(t, list(config.INITIAL_CONDITIONS.values()))
        
        # Generate plot
        fig = _generate_plot(plot_type, t, results)
        plot_data = _fig_to_base64(fig)
        
        return JSONResponse(content={"success": True, "plot": plot_data})
    
    except Exception as e:
        logger.error(f"Plot generation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/download-results")
async def download_results():
    """Generate and return simulation results as a CSV file."""
    try:
        # Create time points and run simulation
        t = np.linspace(0, config.SIMULATION_TIME["end"], config.SIMULATION_TIME["steps"])
        results = model.simulate(t, list(config.INITIAL_CONDITIONS.values()))
        
        # Create DataFrame
        df = pd.DataFrame({
            'Time': t,
            'Viral_Load': results[:, 0],
            'Infected_Cells': results[:, 1],
            'T_Cells': results[:, 2],
            'Antibodies': results[:, 3]
        })
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            df.to_csv(tmp.name, index=False)
            return FileResponse(
                tmp.name,
                media_type='text/csv',
                filename='simulation_results.csv'
            )
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

def _generate_plot(plot_type: str, t: np.ndarray, results: np.ndarray):
    """Generate specified plot type."""
    if plot_type == "linear":
        return plotter.plot_results(t, results)
    elif plot_type == "log":
        return plotter.plot_log_scale(t, results)
    elif plot_type == "phase":
        return plotter.plot_phase_space(results)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")

def _fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Resource not found"}
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )