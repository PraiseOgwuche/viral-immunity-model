// script.js

class ViralModelSimulation {
    constructor() {
        this.chart = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Parameter sliders
        document.querySelectorAll('input[type="range"]').forEach(slider => {
            slider.addEventListener('input', (e) => {
                const valueDisplay = document.getElementById(`${e.target.id}Value`);
                if (valueDisplay) {
                    valueDisplay.textContent = e.target.value;
                }
            });
        });

        // Run simulation button
        const runButton = document.getElementById('runSimulation');
        if (runButton) {
            runButton.addEventListener('click', () => this.runSimulation());
        }

        // Download results button
        const downloadButton = document.getElementById('downloadResults');
        if (downloadButton) {
            downloadButton.addEventListener('click', () => this.downloadResults());
        }
    }

    async runSimulation() {
        const runButton = document.getElementById('runSimulation');
        runButton.disabled = true;
        runButton.textContent = 'Running...';

        try {
            console.log('Starting simulation request...');
            
            // Get parameters
            const params = {
                duration: parseFloat(document.getElementById('duration').value) || 30,
                plot_type: document.getElementById('plotType').value || 'linear',
                beta: parseFloat(document.getElementById('beta').value) || 0.5,
                delta: parseFloat(document.getElementById('delta').value) || 0.7,
                k_t: parseFloat(document.getElementById('k_t').value) || 0.5,
                k_a: parseFloat(document.getElementById('k_a').value) || 0.5
            };

            console.log('Parameters:', params);

            // Make API request
            const response = await fetch('/api/run-simulation?' + new URLSearchParams(params).toString());
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received data:', data);

            if (!data.success) {
                throw new Error(data.error || 'Unknown error occurred');
            }

            // Update visualization
            this.updateVisualization(data.data);
            this.updateMetrics(data.metrics);

        } catch (error) {
            console.error('Detailed simulation error:', error);
            alert('Failed to run simulation. Check console for details.');
        } finally {
            runButton.disabled = false;
            runButton.textContent = 'Run Simulation';
        }
    }

    updateVisualization(data) {
        console.log('Updating visualization with data:', data);
        
        const ctx = document.getElementById('mainChart');
        if (!ctx) {
            console.error('Chart canvas not found');
            return;
        }

        if (this.chart) {
            this.chart.destroy();
        }

        const plotType = document.getElementById('plotType').value;
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.time,
                datasets: [
                    {
                        label: 'Viral Load (V)',
                        data: data.viral_load,
                        borderColor: '#FF4B4B',
                        tension: 0.1
                    },
                    {
                        label: 'Infected Cells (I)',
                        data: data.infected_cells,
                        borderColor: '#4B4BFF',
                        tension: 0.1
                    },
                    {
                        label: 'CD8+ T Cells (T)',
                        data: data.t_cells,
                        borderColor: '#4BFF4B',
                        tension: 0.1
                    },
                    {
                        label: 'Antibodies (A)',
                        data: data.antibodies,
                        borderColor: '#FF4BFF',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 750
                },
                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Time (days)'
                        }
                    },
                    y: {
                        type: plotType === 'log' ? 'logarithmic' : 'linear',
                        title: {
                            display: true,
                            text: 'Population'
                        },
                        min: 0
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                }
            }
        });
    }

    updateMetrics(metrics) {
        console.log('Updating metrics:', metrics);
        
        const fields = {
            'peakViral': metrics.peak_viral_load?.toExponential(2) || '-',
            'clearanceTime': metrics.clearance_time?.toFixed(1) || '-',
            'maxTcell': metrics.max_t_cells?.toExponential(2) || '-',
            'peakAntibody': metrics.peak_antibodies?.toExponential(2) || '-'
        };

        for (const [id, value] of Object.entries(fields)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }
    }
}

// Initialize the simulation when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing simulation...');
    new ViralModelSimulation();
});