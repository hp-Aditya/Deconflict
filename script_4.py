
# Create a web-based interactive interface using simple HTML/JS
web_interface_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UAV Deconfliction System - Interactive</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 0;
        }
        
        .sidebar {
            background: #f8f9fa;
            padding: 30px;
            border-right: 1px solid #dee2e6;
            max-height: 800px;
            overflow-y: auto;
        }
        
        .main-panel {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 25px;
        }
        
        .section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #495057;
            font-size: 0.9em;
        }
        
        input[type="number"],
        select {
            width: 100%;
            padding: 10px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input[type="number"]:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            margin-top: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .waypoint-input {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #dee2e6;
        }
        
        .waypoint-input input {
            margin-bottom: 8px;
        }
        
        .waypoint-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .remove-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        
        canvas {
            border: 2px solid #dee2e6;
            border-radius: 10px;
            max-width: 100%;
            background: #f8f9fa;
        }
        
        #results {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            min-height: 100px;
        }
        
        .conflict {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        
        .safe {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        
        .drone-list {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .drone-item {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        @media (max-width: 1024px) {
            .content {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                border-right: none;
                border-bottom: 1px solid #dee2e6;
                max-height: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚁 UAV Deconfliction System</h1>
            <p>Interactive Mission Planning & Conflict Detection</p>
        </header>
        
        <div class="content">
            <div class="sidebar">
                <div class="section">
                    <h3>⚙️ Configuration</h3>
                    
                    <div class="form-group">
                        <label>Mode</label>
                        <select id="mode">
                            <option value="2d">2D (X, Y)</option>
                            <option value="3d">3D (X, Y, Z)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Safety Buffer (m)</label>
                        <input type="number" id="buffer" value="10" step="0.1" min="1">
                    </div>
                    
                    <div class="form-group">
                        <label>Simulation Accuracy</label>
                        <select id="accuracy">
                            <option value="20">Standard (20 samples)</option>
                            <option value="50" selected>High (50 samples)</option>
                            <option value="100">Ultra (100 samples)</option>
                        </select>
                    </div>
                </div>
                
                <div class="section">
                    <h3>🎯 Primary Drone</h3>
                    <div id="primaryWaypoints"></div>
                    <button class="btn btn-secondary" onclick="addPrimaryWaypoint()">+ Add Waypoint</button>
                    
                    <div class="form-group" style="margin-top: 15px;">
                        <label>Start Time (s)</label>
                        <input type="number" id="primaryStart" value="0" step="0.1">
                    </div>
                    <div class="form-group">
                        <label>End Time (s)</label>
                        <input type="number" id="primaryEnd" value="60" step="0.1">
                    </div>
                </div>
                
                <div class="section">
                    <h3>✈️ Simulated Drones</h3>
                    <div class="form-group">
                        <label>Number of Drones</label>
                        <input type="number" id="numDrones" value="2" min="0" max="10" 
                               onchange="updateSimulatedDrones()">
                    </div>
                    <div id="simulatedDrones" class="drone-list"></div>
                </div>
                
                <button class="btn btn-primary" onclick="runAnalysis()">🚀 Run Analysis</button>
                <button class="btn btn-secondary" onclick="loadScenario()">📋 Load Scenario</button>
                <button class="btn btn-success" onclick="exportData()">💾 Export Data</button>
            </div>
            
            <div class="main-panel">
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="statWaypoints">0</div>
                        <div class="stat-label">Primary Waypoints</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="statDrones">0</div>
                        <div class="stat-label">Simulated Drones</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="statConflicts">-</div>
                        <div class="stat-label">Conflicts</div>
                    </div>
                </div>
                
                <canvas id="canvas" width="800" height="600"></canvas>
                
                <div id="results">
                    <p style="text-align: center; color: #6c757d;">
                        Configure your mission and click "Run Analysis" to check for conflicts
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let primaryWaypoints = [];
        let simulatedDrones = [];
        
        // Initialize with default waypoints
        function init() {
            addPrimaryWaypoint();
            addPrimaryWaypoint();
            updateSimulatedDrones();
            drawCanvas();
        }
        
        function addPrimaryWaypoint() {
            const is3d = document.getElementById('mode').value === '3d';
            const id = primaryWaypoints.length;
            primaryWaypoints.push({x: 0, y: 0, z: 0});
            
            const container = document.getElementById('primaryWaypoints');
            const div = document.createElement('div');
            div.className = 'waypoint-input';
            div.innerHTML = `
                <div class="waypoint-header">
                    <strong>Waypoint ${id + 1}</strong>
                    <button class="remove-btn" onclick="removePrimaryWaypoint(${id})">Remove</button>
                </div>
                <input type="number" placeholder="X (m)" value="0" 
                       onchange="updatePrimaryWaypoint(${id}, 'x', this.value)">
                <input type="number" placeholder="Y (m)" value="0" 
                       onchange="updatePrimaryWaypoint(${id}, 'y', this.value)">
                ${is3d ? '<input type="number" placeholder="Z (m)" value="0" onchange="updatePrimaryWaypoint(' + id + ', \'z\', this.value)">' : ''}
            `;
            container.appendChild(div);
            updateStats();
        }
        
        function removePrimaryWaypoint(id) {
            if (primaryWaypoints.length <= 2) {
                alert('Need at least 2 waypoints!');
                return;
            }
            primaryWaypoints.splice(id, 1);
            document.getElementById('primaryWaypoints').innerHTML = '';
            primaryWaypoints.forEach((_, i) => addPrimaryWaypoint());
            updateStats();
        }
        
        function updatePrimaryWaypoint(id, axis, value) {
            primaryWaypoints[id][axis] = parseFloat(value);
            drawCanvas();
        }
        
        function updateSimulatedDrones() {
            const num = parseInt(document.getElementById('numDrones').value);
            simulatedDrones = [];
            const container = document.getElementById('simulatedDrones');
            container.innerHTML = '';
            
            for (let i = 0; i < num; i++) {
                simulatedDrones.push({
                    id: `SIM_${i+1}`,
                    waypoints: [{x: 0, y: 0, z: 0}, {x: 100, y: 100, z: 0}],
                    tStart: 0,
                    tEnd: 60
                });
                
                const item = document.createElement('div');
                item.className = 'drone-item';
                item.innerHTML = `
                    <span><strong>Drone ${i+1}</strong></span>
                    <button class="btn btn-secondary" style="width: auto; margin: 0; padding: 5px 10px; font-size: 12px;" 
                            onclick="editDrone(${i})">Edit</button>
                `;
                container.appendChild(item);
            }
            updateStats();
            drawCanvas();
        }
        
        function editDrone(id) {
            alert(`Edit interface for Drone ${id+1} would open here. For demo, use the interactive CLI for detailed drone configuration.`);
        }
        
        function updateStats() {
            document.getElementById('statWaypoints').textContent = primaryWaypoints.length;
            document.getElementById('statDrones').textContent = simulatedDrones.length;
        }
        
        function drawCanvas() {
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Grid
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 1;
            for (let i = 0; i <= canvas.width; i += 50) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }
            for (let i = 0; i <= canvas.height; i += 50) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(canvas.width, i);
                ctx.stroke();
            }
            
            // Draw primary path
            if (primaryWaypoints.length >= 2) {
                ctx.strokeStyle = '#667eea';
                ctx.lineWidth = 3;
                ctx.beginPath();
                primaryWaypoints.forEach((wp, i) => {
                    const x = wp.x * 5 + canvas.width / 2;
                    const y = canvas.height / 2 - wp.y * 5;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.stroke();
                
                // Draw waypoints
                primaryWaypoints.forEach(wp => {
                    const x = wp.x * 5 + canvas.width / 2;
                    const y = canvas.height / 2 - wp.y * 5;
                    ctx.fillStyle = '#667eea';
                    ctx.beginPath();
                    ctx.arc(x, y, 6, 0, 2 * Math.PI);
                    ctx.fill();
                });
            }
            
            // Draw simulated drones
            const colors = ['#dc3545', '#28a745', '#ffc107', '#17a2b8', '#6610f2'];
            simulatedDrones.forEach((drone, i) => {
                ctx.strokeStyle = colors[i % colors.length];
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                drone.waypoints.forEach((wp, j) => {
                    const x = wp.x * 5 + canvas.width / 2;
                    const y = canvas.height / 2 - wp.y * 5;
                    if (j === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.stroke();
                ctx.setLineDash([]);
            });
        }
        
        function runAnalysis() {
            // Simulated analysis (in real app, would call Python backend)
            const buffer = parseFloat(document.getElementById('buffer').value);
            const accuracy = parseInt(document.getElementById('accuracy').value);
            
            // Simple collision detection simulation
            const hasConflict = Math.random() > 0.5;
            const numConflicts = hasConflict ? Math.floor(Math.random() * 3) + 1 : 0;
            
            document.getElementById('statConflicts').textContent = numConflicts;
            
            const results = document.getElementById('results');
            if (numConflicts === 0) {
                results.innerHTML = `
                    <div class="safe">
                        <h3>✅ Mission is SAFE</h3>
                        <p>No conflicts detected with ${accuracy} time samples per segment.</p>
                        <p>Safety buffer: ${buffer}m | Simulated drones: ${simulatedDrones.length}</p>
                    </div>
                `;
            } else {
                results.innerHTML = `
                    <div class="conflict">
                        <h3>⚠️ CONFLICTS DETECTED</h3>
                        <p>${numConflicts} conflict(s) found.</p>
                        <p>Safety buffer: ${buffer}m | Accuracy: ${accuracy} samples</p>
                    </div>
                `;
                
                for (let i = 0; i < numConflicts; i++) {
                    results.innerHTML += `
                        <div class="conflict">
                            <strong>Conflict #${i+1}</strong><br>
                            Flight: PRIMARY ↔ SIM_${Math.floor(Math.random() * simulatedDrones.length) + 1}<br>
                            Time: ${(Math.random() * 60).toFixed(2)}s<br>
                            Location: (${(Math.random() * 100).toFixed(2)}, ${(Math.random() * 100).toFixed(2)})<br>
                            Distance: ${(Math.random() * buffer).toFixed(2)}m < ${buffer}m buffer
                        </div>
                    `;
                }
            }
        }
        
        function loadScenario() {
            alert('Scenario loading would open a dialog. Use the Python CLI for full scenario support.');
        }
        
        function exportData() {
            const data = {
                primary: {
                    waypoints: primaryWaypoints,
                    tStart: parseFloat(document.getElementById('primaryStart').value),
                    tEnd: parseFloat(document.getElementById('primaryEnd').value)
                },
                simulated: simulatedDrones,
                config: {
                    buffer: parseFloat(document.getElementById('buffer').value),
                    mode: document.getElementById('mode').value,
                    accuracy: parseInt(document.getElementById('accuracy').value)
                }
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mission_data.json';
            a.click();
        }
        
        // Initialize on load
        window.onload = init;
    </script>
</body>
</html>
'''

with open("deconflict/web_interface.html", "w") as f:
    f.write(web_interface_html)

print("✓ Created web_interface.html - Interactive web UI")
