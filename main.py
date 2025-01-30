import streamlit as st
import requests
import streamlit.components.v1 as components
import json

# Fetch astronomical data
a = requests.get('https://api.visibleplanets.dev/v3?latitude=32&longitude=-98', verify=False)
data = dict(a.json())

# Display data
st.title("Orientation")

# JavaScript for Device Orientation and Camera Access
orientation_js = """
<script>
function getOrientation() {
    if (window.DeviceOrientationEvent) {
        window.addEventListener('deviceorientation', function(event) {
            var alpha = event.alpha.toFixed(2);
            var beta = event.beta.toFixed(2);
            var gamma = event.gamma.toFixed(2);
            document.getElementById('orientation').innerText = `Alpha: ${alpha}, Beta: ${beta}, Gamma: ${gamma}`;
            updatePlanetPositions(alpha, beta, gamma);
        }, false);
    } else {
        document.getElementById('orientation').innerText = "Device orientation not supported.";
    }
}
getOrientation();

// Access the back camera
async function startCamera() {
    try {
        const constraints = {
            video: {
                facingMode: { exact: "environment" } // Use "environment" for back camera
            }
        };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        const videoElement = document.getElementById('video');
        videoElement.srcObject = stream;
    } catch (error) {
        console.error('Error accessing the camera', error);
    }
}

startCamera();

// Update planet positions based on device orientation
function updatePlanetPositions(alpha, beta, gamma) {
    const planets = JSON.parse(document.getElementById('planetData').innerText);
    planets.forEach(planet => {
        // Calculate screen position based on alpha, beta, gamma
        // This is a simplified example, you may need more complex calculations
        const x = (alpha / 360) * window.innerWidth;
        const y = (beta / 180) * window.innerHeight;
        const planetElement = document.getElementById(planet.name);
        planetElement.style.left = `${x}px`;
        planetElement.style.top = `${y}px`;
    });
}
</script>
<div id="orientation" style="width: 100%; height: 100%;"></div>
<video id="video" autoplay width=100% height=100%></video>
<div id="planetOverlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    <!-- Planet positions will be updated here -->
    <div id="planetData" style="display: none;">{data}</div>
    {planets_html}
</div>
"""

# Generate HTML for planets
planets_html = ""
for obj in data['data']:
    planets_html += f'<div id="{obj["name"]}" style="position: absolute; color: white;">{obj["name"]}</div>'
st.write(planets_html)

# Embed the JavaScript and HTML into the Streamlit app
components.html(orientation_js.replace("{data}", json.dumps(data['data'])).replace("{planets_html}", planets_html), height=500)
