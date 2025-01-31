import streamlit as st
import streamlit.components.v1 as components

st.title("Orientation")

# JavaScript for Device Orientation, Camera Access, and API Call
orientation_js = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    // Initialize scene, camera, and renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Function to calculate FOV
    function calculateFOV() {
      // Get the aspect ratio (width / height)
      const aspectRatio = window.innerWidth / window.innerHeight;

      // Get the camera's vertical FOV (in degrees)
      const verticalFOV = camera.fov; // This is in degrees

      // Convert vertical FOV to radians
      const verticalFOVRad = THREE.MathUtils.degToRad(verticalFOV);

      // Calculate the horizontal FOV using the formula
      const horizontalFOVRad = 2 * Math.atan(Math.tan(verticalFOVRad / 2) * aspectRatio);

      // Convert horizontal FOV back to degrees
      const horizontalFOV = THREE.MathUtils.radToDeg(horizontalFOVRad);

      // Output the FOV values
      console.log(`Vertical FOV: ${verticalFOV}°`);
      console.log(`Horizontal FOV: ${horizontalFOV.toFixed(2)}°`);
      document.getElementById('fov').innerText += verticalFOV;
      document.getElementById('fov').innerText += horizontalFOV.toFixed(2);
    }

    // Update the camera on window resize
    window.addEventListener('resize', () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      calculateFOV();  // Recalculate FOV after resize
    });

    // Example render loop
    function animate() {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    }

    // Initial FOV calculation
    calculateFOV();
    
    // Start the render loop
    animate();
  </script>
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

function calculateScreenPosition(azimuth, altitude, alpha, beta, gamma) {
    // Convert azimuth and altitude to radians
    const azimuthRad = azimuth * (Math.PI / 180);
    const altitudeRad = altitude * (Math.PI / 180);

    // Calculate the screen position based on device orientation
    const x = (alpha / 360) * window.innerWidth;
    const y = (beta / 180) * window.innerHeight;

    // Adjust the position based on azimuth and altitude
    const adjustedX = x + (azimuthRad * window.innerWidth / (2 * Math.PI));
    const adjustedY = y - (altitudeRad * window.innerHeight / (2 * Math.PI));

    return { x: adjustedX, y: adjustedY };
}

// Update planet positions based on device orientation
function updatePlanetPositions(alpha, beta, gamma) {
    const planets = JSON.parse(document.getElementById('planetData').innerText);
    planets.forEach(planet => {
        const { azimuth, altitude } = planet;
        const position = calculateScreenPosition(azimuth, altitude, alpha, beta, gamma);
        const planetElement = document.getElementById(planet.name);
        planetElement.style.left = `${position.x}px`;
        planetElement.style.top = `${position.y}px`;
    });
}

// Get user's latitude and longitude
navigator.geolocation.getCurrentPosition(async function(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    // Fetch astronomical data
    const response = await fetch(`https://api.visibleplanets.dev/v3?latitude=${latitude}&longitude=${longitude}`);
    const data = await response.json();

    // Display the response data in the UI
    document.getElementById('responseData').innerText = JSON.stringify(data, null, 2);
    // Display planet data
    document.getElementById('planetData').innerText = JSON.stringify(data.data);
    // Create divs for each planet
    const planetOverlay = document.getElementById('planetOverlay');
    data.data.forEach(planet => {
        const planetDiv = document.createElement('div');
        planetDiv.id = planet.name;
        planetDiv.style.position = 'absolute';
        planetDiv.style.color = 'white';
        planetDiv.innerText = planet.name;
        planetOverlay.appendChild(planetDiv);
    });
    updatePlanetPositions(0, 0, 0); // Initial update
});
</script>
<div id="orientation" style="background-color: #f0f0f0; padding: 10px;"></div>
<div id="fov" style="background-color: #f0f0f0; padding: 10px;"></div>
<video id="video" autoplay width=100% height=100%></video>
<div id="planetOverlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    <!-- Planet positions will be updated here -->
    <div id="planetData" style="display: none;"></div>
</div>
<pre id="responseData" style="background-color: #f0f0f0; padding: 10px;"></pre>
"""

# Embed the JavaScript and HTML into the Streamlit app
components.html(orientation_js, height=1600)
