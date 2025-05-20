from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Union
import json
from pathlib import Path
import os

app = FastAPI(title="State Editor")

# Load state data
state_file = Path("quam_state/state.json")
last_modified_time = 0

class QubitData(BaseModel):
    amplitude: float
    length: int
    resonator_if: float
    xy_if: float

class StateUpdate(BaseModel):
    qubits: Dict[str, QubitData]

def load_state():
    global last_modified_time
    current_mtime = os.path.getmtime(state_file)
    if current_mtime != last_modified_time:
        last_modified_time = current_mtime
    with open(state_file, 'r') as f:
        return json.load(f)

def save_state(data):
    with open(state_file, 'w') as f:
        json.dump(data, f, indent=4)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>State Editor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .table-container {
                margin: 20px;
            }
            .status-message {
                margin: 10px;
                padding: 10px;
                border-radius: 5px;
            }
            .success {
                background-color: #d4edda;
                color: #155724;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
            }
            .shortcut-hint {
                color: #6c757d;
                font-size: 0.9em;
                margin-bottom: 20px;
            }
            .auto-refresh-toggle {
                margin: 10px 0;
            }
            .active-indicator {
                color: #28a745;
                margin-left: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mt-4">State Editor</h1>
            <div class="shortcut-hint">
                Press <kbd>Ctrl</kbd> + <kbd>S</kbd> to save changes
            </div>
            <div class="auto-refresh-toggle">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="autoRefreshToggle" checked>
                    <label class="form-check-label" for="autoRefreshToggle">Auto-refresh (every 2 seconds)</label>
                </div>
            </div>
            <div id="status-message" class="status-message" style="display: none;"></div>
            <div class="table-container">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Qubit</th>
                            <th>Readout Amplitude</th>
                            <th>Readout Length</th>
                            <th>Resonator IF</th>
                            <th>XY IF</th>
                        </tr>
                    </thead>
                    <tbody id="qubit-table">
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            let qubitData = {};
            let autoRefreshInterval = null;
            let isAutoRefreshEnabled = true;

            function startAutoRefresh() {
                if (autoRefreshInterval) return;
                autoRefreshInterval = setInterval(checkForUpdates, 2000);
            }

            function stopAutoRefresh() {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
            }

            async function checkForUpdates() {
                try {
                    const response = await fetch('/api/check-updates');
                    const data = await response.json();
                    if (data.modified) {
                        await loadData();
                        showStatus('Data refreshed from external changes', 'success');
                    }
                } catch (error) {
                    console.error('Error checking for updates:', error);
                }
            }

            async function loadData() {
                try {
                    const response = await fetch('/api/qubits');
                    qubitData = await response.json();
                    updateTable();
                } catch (error) {
                    showStatus('Error loading data: ' + error, 'error');
                }
            }

            function updateTable() {
                const tbody = document.getElementById('qubit-table');
                tbody.innerHTML = '';
                
                for (const [qubitId, data] of Object.entries(qubitData)) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${qubitId}${data.active ? '<span class="active-indicator">✓</span>' : ''}</td>
                        <td><input type="number" step="any" value="${data.amplitude}" 
                            onchange="updateValue('${qubitId}', 'amplitude', this.value)"></td>
                        <td><input type="number" step="1" value="${data.length}" 
                            onchange="updateValue('${qubitId}', 'length', this.value)"></td>
                        <td><input type="number" step="any" value="${data.resonator_if}" 
                            onchange="updateValue('${qubitId}', 'resonator_if', this.value)"></td>
                        <td><input type="number" step="any" value="${data.xy_if}" 
                            onchange="updateValue('${qubitId}', 'xy_if', this.value)"></td>
                    `;
                    tbody.appendChild(row);
                }
            }

            function updateValue(qubitId, field, value) {
                if (field === 'length') {
                    qubitData[qubitId][field] = parseInt(value);
                } else {
                    qubitData[qubitId][field] = parseFloat(value);
                }
            }

            async function saveChanges() {
                try {
                    const response = await fetch('/api/save', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ qubits: qubitData })
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showStatus('Changes saved successfully!', 'success');
                    } else {
                        showStatus('Error: ' + result.error, 'error');
                    }
                } catch (error) {
                    showStatus('Error saving changes: ' + error, 'error');
                }
            }

            function showStatus(message, type) {
                const statusDiv = document.getElementById('status-message');
                statusDiv.textContent = message;
                statusDiv.className = 'status-message ' + type;
                statusDiv.style.display = 'block';
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 3000);
            }

            // Add auto-refresh toggle functionality
            document.getElementById('autoRefreshToggle').addEventListener('change', function(e) {
                isAutoRefreshEnabled = e.target.checked;
                if (isAutoRefreshEnabled) {
                    startAutoRefresh();
                } else {
                    stopAutoRefresh();
                }
            });

            // Add keyboard shortcut for saving
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 's') {
                    e.preventDefault(); // Prevent browser's save dialog
                    saveChanges();
                }
            });

            // Load data when page loads and start auto-refresh
            loadData();
            startAutoRefresh();
        </script>
    </body>
    </html>
    """

@app.get("/api/qubits")
async def get_qubits():
    state_data = load_state()
    qubits = {}
    active_qubits = set(state_data.get("active_qubit_names", []))
    for qubit_id, qubit_data in state_data["qubits"].items():
        try:
            qubits[qubit_id] = {
                'amplitude': qubit_data["resonator"]["operations"]["readout"]["amplitude"],
                'length': qubit_data["resonator"]["operations"]["readout"]["length"],
                'resonator_if': qubit_data["resonator"]["intermediate_frequency"],
                'xy_if': qubit_data["xy"]["intermediate_frequency"],
                'active': qubit_id in active_qubits
            }
        except KeyError:
            qubits[qubit_id] = {
                'amplitude': 0.0,
                'length': 0.0,
                'resonator_if': 0.0,
                'xy_if': 0.0,
                'active': qubit_id in active_qubits
            }
    return qubits

@app.post("/api/save")
async def save_changes(update: StateUpdate):
    try:
        state_data = load_state()
        
        for qubit_id, values in update.qubits.items():
            try:
                state_data["qubits"][qubit_id]["resonator"]["operations"]["readout"]["amplitude"] = values.amplitude
                state_data["qubits"][qubit_id]["resonator"]["operations"]["readout"]["length"] = values.length
                state_data["qubits"][qubit_id]["resonator"]["intermediate_frequency"] = values.resonator_if
                state_data["qubits"][qubit_id]["xy"]["intermediate_frequency"] = values.xy_if
            except KeyError as e:
                raise HTTPException(status_code=400, detail=f"Invalid qubit data for {qubit_id}: {str(e)}")
        
        save_state(state_data)
        return {"message": "Changes saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/check-updates")
async def check_updates():
    current_mtime = os.path.getmtime(state_file)
    return {"modified": current_mtime != last_modified_time} 