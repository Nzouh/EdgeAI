// Sentinel Dashboard Logic - CONNECTED TO REAL C++ BRAIN
const analyzeBtn = document.getElementById('analyze-btn');
const probText = document.getElementById('probability-text');
const probBar = document.getElementById('probability-bar');
const cycleEst = document.getElementById('cycle-est');
const warningText = document.getElementById('warning-text');
const globalStatus = document.getElementById('global-status');

// Helper to update gauge
function updateGauge(percent) {
    const offset = 283 - (percent * 2.83);
    probBar.style.strokeDashoffset = offset;
    probText.innerText = `${(percent).toFixed(2)}%`;
    
    if (percent > 50) {
        probBar.style.stroke = '#ff0055';
        globalStatus.style.color = '#ff0055';
        globalStatus.style.borderColor = '#ff0055';
        globalStatus.innerText = 'DANGER DETECTED';
        warningText.innerText = 'MAINTENANCE REQUIRED IMMEDIATELY';
        cycleEst.innerText = 'CRITICAL (< 5)';
    } else {
        probBar.style.stroke = '#00f2ff';
        globalStatus.style.color = '#00f2ff';
        globalStatus.style.borderColor = '#00f2ff';
        globalStatus.innerText = 'SYSTEM NOMINAL';
        warningText.innerText = 'NO ACTION REQUIRED';
        cycleEst.innerText = 'NOMINAL (>30)';
    }
}

// REAL PRODUCTION INFERENCE CALL
analyzeBtn.addEventListener('click', async () => {
    // Collect 17 sensors (Mocking some for demo, but structure is real)
    const s17 = document.getElementById('s17').value;
    const s2 = document.getElementById('s2').value;
    const s3 = document.getElementById('s3').value;
    
    // Constructing the full 17-sensor row (averaging the other 14 for the demo)
    const sensorRow = [
        643.02, 1585.29, 1398.21, 14.62, 21.61, 
        553.90, 2388.04, 9050.17, 47.20, parseFloat(s2), 
        2388.03, 8133.24, 8.4195, 0.03, 392.0, 
        parseFloat(s3), parseFloat(s17)
    ].join(',');

    analyzeBtn.innerText = "QUERYING C++ ENGINE...";
    analyzeBtn.disabled = true;

    try {
        const response = await fetch('http://localhost:8080/predict', {
            method: 'POST',
            body: sensorRow
        });

        const data = await response.json();
        
        if (data.probability !== undefined) {
            updateGauge(data.probability * 100);
        } else {
            console.error("Engine Error:", data.error);
        }

    } catch (err) {
        console.error("Connection Failed. Did you start the Docker container?");
        alert("CRITICAL: Cannot reach Sentinel C++ Brain. Ensure Docker is running.");
    } finally {
        analyzeBtn.innerText = "RUN SENTINEL ANALYSIS";
        analyzeBtn.disabled = false;
    }
});

// Initial state
updateGauge(0.01);
