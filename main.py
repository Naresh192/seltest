import streamlit as st
import streamlit.components.v1 as components

st.title("Orientation")

# JavaScript for Device Orientation, Camera Access, and API Call
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
        const videoTrack = stream.getVideoTracks()[0];
        const settings = videoTrack.getSettings();
        
        const videoElement = document.getElementById('video');
        videoElement.srcObject = stream;
    } catch (error) {
        console.error('Error accessing the camera', error);
    }
}

startCamera();

function rotateVector(x, y, z, rotationMatrix, pitchMatrix, rollMatrix) {
  // Multiply matrices together to apply all rotations
  const result = multiplyMatrices(rotationMatrix, pitchMatrix, rollMatrix);
  
  // Apply the final rotation
  const rotatedX = result[0][0] * x + result[0][1] * y + result[0][2] * z;
  const rotatedY = result[1][0] * x + result[1][1] * y + result[1][2] * z;
  const rotatedZ = result[2][0] * x + result[2][1] * y + result[2][2] * z;
  
  return [rotatedX, rotatedY, rotatedZ];
}

function multiplyMatrices(m1, m2, m3) {
  // Multiply the three matrices to apply all rotations in sequence
  const intermediate = matrixMultiply(m1, m2);
  return matrixMultiply(intermediate, m3);
}

function matrixMultiply(m1, m2) {
  const result = [];
  for (let i = 0; i < m1.length; i++) {
    result[i] = [];
    for (let j = 0; j < m2[0].length; j++) {
      result[i][j] = 0;
      for (let k = 0; k < m1[0].length; k++) {
        result[i][j] += m1[i][k] * m2[k][j];
      }
    }
  }
  return result;
}



function planetToScreenCoords(azimuth, altitude, alpha, beta, gamma, fovVertical, fovHorizontal) {
    // Convert azimuth and altitude to radians
    const video = document.getElementById('video');
    const windowWidth = video.videoWidth;
    const windowHeight = video.videoHeight;
    const azimuthRad = azimuth * Math.PI / 180;
    const altitudeRad = altitude * Math.PI / 180;
    
    // Step 1: Convert azimuth/altitude to Cartesian coordinates (x, y, z)
    const r = 1; // Assume unit sphere, can scale if needed
    const x = r * Math.cos(altitudeRad) * Math.sin(azimuthRad);
    const y = r * Math.sin(altitudeRad);
    const z = r * Math.cos(altitudeRad) * Math.cos(azimuthRad);
    
    // Step 2: Rotate the coordinates based on the device orientation (alpha, beta, gamma)
    const alphaRad = alpha * Math.PI / 180;
    const betaRad = beta * Math.PI / 180;
    const gammaRad = gamma * Math.PI / 180;
    // Rotation matrices for Euler angles (alpha, beta, gamma)
    const Rz = [
        [Math.cos(alphaRad), -Math.sin(alphaRad), 0],
        [Math.sin(alphaRad), Math.cos(alphaRad), 0],
        [0, 0, 1]
    ];

    const Rx = [
        [1, 0, 0],
        [0, Math.cos(betaRad), -Math.sin(betaRad)],
        [0, Math.sin(betaRad), Math.cos(betaRad)]
    ];

    const Ry = [
        [Math.cos(gammaRad), 0, Math.sin(gammaRad)],
        [0, 1, 0],
        [-Math.sin(gammaRad), 0, Math.cos(gammaRad)]
    ];
    // Combined rotation matrix: R = Rz * Ry * Rx
    const rotationMatrix = multiplyMatrices(multiplyMatrices(Rz, Ry), Rx);
    

    // Rotate the Cartesian coordinates using the rotation matrix
    const rotatedCoords = multiplyMatrixVector(rotationMatrix, [x, y, z]);

    const xRot = rotatedCoords[0];
    const yRot = rotatedCoords[1];
    const zRot = rotatedCoords[2];


    // Step 3: Project the 3D coordinates onto the 2D screen
    const fovVerticalRad = fovVertical * Math.PI / 180;
    const fovHorizontalRad = fovHorizontal * Math.PI / 180;
    
    const screenX = (xRot / zRot) * Math.tan(fovHorizontalRad / 2) * windowWidth / 2 + windowWidth / 2;
    const screenY = -(yRot / zRot) * Math.tan(fovVerticalRad / 2) * windowHeight / 2 + windowHeight / 2;

    // Return the calculated screen coordinates
    document.getElementById('pov').innerText = screenX
    return { x: screenX, y: screenY };
}

function calculateScreenPosition(azimuth, altitude, alpha, beta, gamma, fovVertical,fovHorizontal) {
    windowWidth = window.innerWidth;
    windowHeight = window.innerHeight;
    // Convert azimuth and altitude to radians
    const azimuthRad = azimuth * Math.PI / 180;
    const altitudeRad = altitude * Math.PI / 180;
    
    // Step 1: Convert azimuth/altitude to Cartesian coordinates (x, y, z)
    const r = 1; // Assume unit sphere, can scale if needed
    const x = r * Math.cos(altitudeRad) * Math.sin(azimuthRad);
    const y = r * Math.sin(altitudeRad);
    const z = r * Math.cos(altitudeRad) * Math.cos(azimuthRad);
    
    // Step 2: Rotate the coordinates based on the device orientation (alpha, beta, gamma)
    const alphaRad = alpha * Math.PI / 180;
    const betaRad = beta * Math.PI / 180;
    const gammaRad = gamma * Math.PI / 180;
    // Rotation matrices for Euler angles (alpha, beta, gamma)
    const Rz = [
        [Math.cos(alphaRad), -Math.sin(alphaRad), 0],
        [Math.sin(alphaRad), Math.cos(alphaRad), 0],
        [0, 0, 1]
    ];

    const Rx = [
        [1, 0, 0],
        [0, Math.cos(betaRad), -Math.sin(betaRad)],
        [0, Math.sin(betaRad), Math.cos(betaRad)]
    ];

    const Ry = [
        [Math.cos(gammaRad), 0, Math.sin(gammaRad)],
        [0, 1, 0],
        [-Math.sin(gammaRad), 0, Math.cos(gammaRad)]
    ];
    // Combined rotation matrix: R = Rz * Ry * Rx
    const rotationMatrix = multiplyMatrices(multiplyMatrices(Rz, Ry), Rx);
    

    // Rotate the Cartesian coordinates using the rotation matrix
    const rotatedCoords = multiplyMatrixVector(rotationMatrix, [x, y, z]);

    const xRot = rotatedCoords[0];
    const yRot = rotatedCoords[1];
    const zRot = rotatedCoords[2];


    // Step 3: Project the 3D coordinates onto the 2D screen
    const fovVerticalRad = fovVertical * Math.PI / 180;
    const fovHorizontalRad = fovHorizontal * Math.PI / 180;
    
    const screenX = (xRot / zRot) * Math.tan(fovHorizontalRad / 2) * windowWidth / 2 + windowWidth / 2;
    const screenY = -(yRot / zRot) * Math.tan(fovVerticalRad / 2) * windowHeight / 2 + windowHeight / 2;

    // Return the calculated screen coordinates
    return { x: screenX, y: screenY };
}

// Update planet positions based on device orientation
function updatePlanetPositions(alpha, beta, gamma) {
    const planets = JSON.parse(document.getElementById('planetData').innerText);
    planets.forEach(planet => {
        const { azimuth, altitude } = planet;
        const position = planetToScreenCoords(azimuth, altitude, alpha, beta, gamma, 56, 70);
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
<div id="pov" style="background-color: red; padding: 10px;"></div>

<video id="video" autoplay width=100% height=100%></video>
<div id="planetOverlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    <!-- Planet positions will be updated here -->
    <div id="planetData" style="display: none;"></div>
</div>
<pre id="responseData" style="background-color: #f0f0f0; padding: 10px;"></pre>
"""

# Embed the JavaScript and HTML into the Streamlit app
components.html(orientation_js, height=1600)
