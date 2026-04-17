// Sentinel Dashboard Logic — Full 17-Axis Control
const analyzeBtn = document.getElementById('analyze-btn');
const probText = document.getElementById('probability-text');
const probBar = document.getElementById('probability-bar');
const cycleEst = document.getElementById('cycle-est');
const warningText = document.getElementById('warning-text');
const globalStatus = document.getElementById('global-status');

// Sensor order must match C++ engine: [s2, s3, s4, s5, s6, s7, s8, s9, s11, s12, s13, s14, s15, s16, s17, s20, s21]
const SLIDER_IDS = ['s2', 's3', 's4', 's7', 's8', 's9', 's11', 's12', 's13', 's14', 's15', 's17', 's20', 's21'];
const FIXED_SENSORS = { s5: 14.62, s6: 21.61, s16: 0.03 };

// Training mean values (nominal)
const NOMINAL = {
    s2: 642.68, s3: 1590.5, s4: 1409.0, s7: 553.4, s8: 2388.1, s9: 9065.2,
    s11: 47.5, s12: 521.4, s13: 2388.1, s14: 8143.8, s15: 8.44, s17: 393.0,
    s20: 38.8, s21: 23.29
};

// High-wear / failure signature values (from engines near RUL=0)
const FAILURE = {
    s2: 644.5, s3: 1616.0, s4: 1441.0, s7: 550.0, s8: 2388.5, s9: 9240.0,
    s11: 48.5, s12: 518.7, s13: 2388.5, s14: 8100.0, s15: 8.58, s17: 400.0,
    s20: 38.2, s21: 22.9
};

// Live slider value display
SLIDER_IDS.forEach(id => {
    const slider = document.getElementById(id);
    const valDisplay = document.getElementById(id + '-val');
    slider.addEventListener('input', () => {
        valDisplay.textContent = parseFloat(slider.value).toFixed(2);
    });
});

// Set all sliders to a preset
function applyPreset(preset) {
    SLIDER_IDS.forEach(id => {
        const slider = document.getElementById(id);
        slider.value = preset[id];
        document.getElementById(id + '-val').textContent = parseFloat(preset[id]).toFixed(2);
    });
}

document.getElementById('btn-nominal').addEventListener('click', () => applyPreset(NOMINAL));
document.getElementById('btn-failure').addEventListener('click', () => applyPreset(FAILURE));

// Gauge update
function updateGauge(percent) {
    const offset = 283 - (percent * 2.83);
    probBar.style.strokeDashoffset = offset;
    probText.innerText = `${(percent).toFixed(2)}%`;
    
    if (percent > 50) {
        probBar.style.stroke = '#ff0055';
        globalStatus.style.color = '#ff0055';
        globalStatus.style.borderColor = '#ff0055';
        globalStatus.style.background = 'rgba(255, 0, 85, 0.1)';
        globalStatus.innerText = 'DANGER DETECTED';
        warningText.innerText = 'MAINTENANCE REQUIRED IMMEDIATELY';
        cycleEst.innerText = 'CRITICAL (< 30)';
    } else {
        probBar.style.stroke = '#00f2ff';
        globalStatus.style.color = '#00f2ff';
        globalStatus.style.borderColor = '#00f2ff';
        globalStatus.style.background = 'rgba(0, 242, 255, 0.1)';
        globalStatus.innerText = 'SYSTEM NOMINAL';
        warningText.innerText = 'NO ACTION REQUIRED';
        cycleEst.innerText = 'NOMINAL (>30)';
    }
}

// Build 17-element sensor array in engine order
function buildSensorRow() {
    const s2 = parseFloat(document.getElementById('s2').value);
    const s3 = parseFloat(document.getElementById('s3').value);
    const s4 = parseFloat(document.getElementById('s4').value);
    const s7 = parseFloat(document.getElementById('s7').value);
    const s8 = parseFloat(document.getElementById('s8').value);
    const s9 = parseFloat(document.getElementById('s9').value);
    const s11 = parseFloat(document.getElementById('s11').value);
    const s12 = parseFloat(document.getElementById('s12').value);
    const s13 = parseFloat(document.getElementById('s13').value);
    const s14 = parseFloat(document.getElementById('s14').value);
    const s15 = parseFloat(document.getElementById('s15').value);
    const s17 = parseFloat(document.getElementById('s17').value);
    const s20 = parseFloat(document.getElementById('s20').value);
    const s21 = parseFloat(document.getElementById('s21').value);

    // Order: s2, s3, s4, s5, s6, s7, s8, s9, s11, s12, s13, s14, s15, s16, s17, s20, s21
    return [
        s2, s3, s4, FIXED_SENSORS.s5, FIXED_SENSORS.s6,
        s7, s8, s9, s11, s12,
        s13, s14, s15, FIXED_SENSORS.s16, s17,
        s20, s21
    ].join(',');
}

// Inference call
analyzeBtn.addEventListener('click', async () => {
    const sensorRow = buildSensorRow();

    analyzeBtn.innerText = "QUERYING C++ ENGINE...";
    analyzeBtn.disabled = true;

    try {
        const response = await fetch('/predict', {
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
        console.error("Connection Failed:", err);
        alert("CRITICAL: Cannot reach Sentinel C++ Brain. Ensure engine is running.");
    } finally {
        analyzeBtn.innerText = "RUN SENTINEL ANALYSIS";
        analyzeBtn.disabled = false;
    }
});

// Initial state
updateGauge(0.01);
