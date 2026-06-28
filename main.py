import streamlit as st
import streamlit.components.v1 as components

st.title("Orientation")

# JavaScript for Device Orientation, Camera Access, and API Call
orientation_js = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r127/three.min.js"></script>
<script  type='module'>
import { DeviceOrientationControls } from 'https://cdn.jsdelivr.net/npm/three@0.127.0/examples/jsm/controls/DeviceOrientationControls.js';


let orientationAvailable = false;
let orientationChecked = false;

function getOrientation() {
    if (window.DeviceOrientationEvent) {
        window.addEventListener('deviceorientation', function(event) {
            if (!orientationChecked) {
                orientationChecked = true;
                // Check if we're getting actual orientation data (not all null/undefined)
                if (event.alpha !== null || event.beta !== null || event.gamma !== null) {
                    orientationAvailable = true;
                    console.log('Device orientation is available');
                } else {
                    console.log('Device orientation not available (sensors not detected)');
                    document.getElementById('orientation').innerText = "Device orientation sensors not detected. Use manual controls below.";
                }
            }

            if (orientationAvailable) {
                var alpha = event.alpha ? event.alpha.toFixed(2) : '0.00';
                var beta = event.beta ? event.beta.toFixed(2) : '0.00';
                var gamma = event.gamma ? event.gamma.toFixed(2) : '0.00';

                // Only update if we have non-zero values (actual sensor data)
                if (event.alpha !== null || event.beta !== null || event.gamma !== null) {
                    document.getElementById('orientation').innerText = `Alpha: ${alpha}, Beta: ${beta}, Gamma: ${gamma} (Device)`;
                    console.log('Device orientation:', { alpha, beta, gamma });
                    updatePlanetPositions(parseFloat(alpha), parseFloat(beta), parseFloat(gamma));
                    // Update manual sliders to match device orientation
                    document.getElementById('alphaSlider').value = alpha;
                    document.getElementById('betaSlider').value = beta;
                    document.getElementById('gammaSlider').value = gamma;
                    document.getElementById('alphaValue').textContent = alpha;
                    document.getElementById('betaValue').textContent = beta;
                    document.getElementById('gammaValue').textContent = gamma;
                }
            }
        }, false);

        // iOS 13+ requires permission request
        if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
            DeviceOrientationEvent.requestPermission()
                .then(permissionState => {
                    if (permissionState === 'granted') {
                        console.log('Device orientation permission granted');
                    } else {
                        console.log('Device orientation permission denied');
                        document.getElementById('orientation').innerText = "Device orientation permission denied. Use manual controls below.";
                    }
                })
                .catch(console.error);
        }
    } else {
        document.getElementById('orientation').innerText = "Device orientation not supported. Use manual controls below.";
        console.error("Device orientation not supported");
    }

    // If no orientation detected after 2 seconds, show manual controls message
    setTimeout(function() {
        if (!orientationAvailable && !orientationChecked) {
            document.getElementById('orientation').innerText = "No device orientation detected. Use manual controls below.";
            console.log('No device orientation detected after timeout');
        }
    }, 2000);
}
getOrientation();

// Access the back camera
async function startCamera() {
    try {
        const constraints = {
            video: {
                facingMode: "environment" // Use "environment" for back camera (removed 'exact' for better compatibility)
            }
        };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        const videoTrack = stream.getVideoTracks()[0];
        const settings = videoTrack.getSettings();

        const videoElement = document.getElementById('video');
        videoElement.srcObject = stream;
        console.log('Camera started successfully', settings);
    } catch (error) {
        console.error('Error accessing the camera', error);
        document.getElementById('orientation').innerText = 'Camera error: ' + error.message + ' (Using placeholder background)';
        // Set a placeholder background color if camera fails
        document.getElementById('video').style.backgroundColor = '#1a1a2e';
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

async function getPlanetDistance(planetName) {
  const apiUrl = `https://api.le-systeme-solaire.net/rest/bodies/${planetName}`;

  try {
    // Fetch data from the API
    const response = await fetch(apiUrl);
    const data = await response.json();

    // Extract relevant values from the data
    if (data && data.meanRadius) {
      const distance = data.meanRadius; // Distance to Earth in km (this could vary)
      console.log(`The distance to ${planetName} from Earth is approximately: ${distance} km`);
      return distance;
    } else {
      console.log("Data not available or planet does not exist.");
      return null;
    }
  } catch (error) {
    console.error("Error fetching planet data:", error);
  }
}


function sphericalToCartesian(azimuth, altitude) {
    const az = THREE.MathUtils.degToRad(azimuth);
    const alt = THREE.MathUtils.degToRad(altitude);
    return new THREE.Vector3(
        Math.cos(alt) * Math.sin(az),
        Math.sin(alt),
        Math.cos(alt) * Math.cos(az)
    );
}
function applyDeviceRotation(vector, alpha, beta, gamma) {
    const euler = new THREE.Euler(
        THREE.MathUtils.degToRad(beta),
        THREE.MathUtils.degToRad(alpha),
        THREE.MathUtils.degToRad(gamma),
        'YXZ' // Rotation order
    );
    const quaternion = new THREE.Quaternion().setFromEuler(euler);
    return vector.applyQuaternion(quaternion);
}
function projectToScreen(deviceVector, hFov, vFov, width, height) {
    const camera = new THREE.PerspectiveCamera(
      vFov, // in degrees
      width / height,
      0.1,
      1000
    );
    camera.position.set(0, 0, 0);
    camera.lookAt(new THREE.Vector3(0, 0, -1));
    const projected = deviceVector.clone();
    projected.project(camera);
    const screenX = (projected.x + 1) / 2 * width;
    const screenY = (-projected.y + 1) / 2 * height;
    return {
        x: screenX,
        y: screenY,
    };
}
function getScreenPosition(azimuth, altitude, alpha, beta, gamma, hFov, vFov) {
    // Convert azimuth and altitude to radians
    const azRad = THREE.MathUtils.degToRad(azimuth);
    const altRad = THREE.MathUtils.degToRad(altitude);
    // Convert spherical coordinates (azimuth, altitude) to Cartesian coordinates
    const radius = 1; // Unit sphere
    const x = radius * Math.cos(altRad) * Math.sin(azRad); // North
    const y = radius * Math.sin(altRad); // Up
    const z = radius * Math.cos(altRad) * Math.cos(azRad); // East
    // Create a Three.js vector for the planet's position
    const planetPosition = new THREE.Vector3(x, y, z);

    // Create a rotation matrix from device orientation (alpha, beta, gamma)
    const euler = new THREE.Euler(
        THREE.MathUtils.degToRad(beta),  // Tilt front/back (beta)
        THREE.MathUtils.degToRad(alpha), // Compass direction (alpha)
        THREE.MathUtils.degToRad(gamma), // Tilt left/right (gamma)
        'YXZ' // Rotation order
    );

    // Apply the rotation to the planet's position
    planetPosition.applyEuler(euler);

    // Check if the planet is behind the camera (z <= 0)
    if (planetPosition.z <= 0) return null;
    // Convert 3D coordinates to 2D screen coordinates
    const hFovRad = THREE.MathUtils.degToRad(hFov);
    const vFovRad = THREE.MathUtils.degToRad(vFov);

    const scaleX = 1 / Math.tan(hFovRad / 2);
    const scaleY = 1 / Math.tan(vFovRad / 2);

    const screenX = (planetPosition.x / planetPosition.z) * scaleX;
    const screenY = (planetPosition.y / planetPosition.z) * scaleY;

    // Normalize to percentage
    const percentX = (screenX * 0.5 + 0.5) * 100;
    const percentY = (0.5 - screenY * 0.5) * 100;

    // Check if the planet is within the screen bounds
    if (percentX < 0 || percentX > 100 || percentY < 0 || percentY > 100) return null;
    return { x: percentX, y: percentY };
}

function degreesToRadians(deg) {
    return deg * Math.PI / 180;
}

function computeRotationMatrix(alpha, beta, gamma) {
    const degToRad = Math.PI / 180;
    const a = (alpha || 0) * degToRad;
    const b = (beta || 0) * degToRad;
    const c = (gamma || 0) * degToRad;

    const cosA = Math.cos(a), sinA = Math.sin(a);
    const cosB = Math.cos(b), sinB = Math.sin(b);
    const cosC = Math.cos(c), sinC = Math.sin(c);

    // ZXY rotation matrix
    return [
        [
            cosA * cosC - sinA * sinB * sinC,
            -sinA * cosB,
            cosA * sinC + sinA * sinB * cosC
        ],
        [
            sinA * cosC + cosA * sinB * sinC,
            cosA * cosB,
            sinA * sinC - cosA * sinB * cosC
        ],
        [
            -cosB * sinC,
            sinB,
            cosB * cosC
        ]
    ];
}

function matrixVectorMultiply(m, v) {
    return [
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]
    ];
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
    const planetDataElement = document.getElementById('planetData');
    if (!planetDataElement || !planetDataElement.innerText) {
        console.log('Planet data not yet loaded');
        return;
    }

    const planets = JSON.parse(planetDataElement.innerText);
    console.log('Updating positions for', planets.length, 'planets');
    console.log('Device orientation:', { alpha, beta, gamma });

    planets.forEach(planet => {
        const { azimuth, altitude, meanradius } = planet;
        console.log(`Planet ${planet.name}: azimuth=${azimuth}, altitude=${altitude}`);
        const screenPos = getScreenPosition(azimuth, altitude, alpha, beta, gamma, 70, 56);
        if (screenPos) {
            const planetElement = document.getElementById(planet.name);
            if (planetElement) {
                planetElement.style.left = `${screenPos.x}%`;
                planetElement.style.top = `${screenPos.y}%`;
                planetElement.style.display = 'block';
                console.log(`Positioned ${planet.name} at ${screenPos.x}%, ${screenPos.y}%`);
            }
        } else {
            const planetElement = document.getElementById(planet.name);
            if (planetElement) {
                planetElement.style.display = 'none';
                console.log(`${planet.name} is not visible`);
            }
        }
    });
}

// Get user's latitude and longitude
navigator.geolocation.getCurrentPosition(async function(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    console.log('Location obtained:', { latitude, longitude });
    fetchPlanetData(latitude, longitude);
}, function(error) {
    console.error('Geolocation error:', error);
    document.getElementById('orientation').innerText = 'Geolocation error: ' + error.message + ' (Using default location: New York)';
    // Use default location (New York) if geolocation fails
    fetchPlanetData(40.7128, -74.0060);
});

async function fetchPlanetData(latitude, longitude) {
    try {
        const response = await fetch(`https://api.visibleplanets.dev/v3?latitude=${latitude}&longitude=${longitude}`);
        const data = await response.json();
        console.log('Planet data fetched:', data);

        for (let planet of data.data) {
            const planetName = planet.name.toLowerCase(); // Ensure planet name is in lowercase for the API
            const bodyResponse = await fetch(`https://api.le-systeme-solaire.net/rest/bodies/${planetName}`);
            const bodyData = await bodyResponse.json();

            // Add 'meanradius' to the planet object
            planet.meanradius = bodyData.meanRadius || 'N/A';  // Add meanradius, if available
        }
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
            planetDiv.style.fontSize = '20px';
            planetDiv.style.fontWeight = 'bold';
            planetDiv.style.textShadow = '2px 2px 4px rgba(0,0,0,0.8)';
            planetDiv.innerText = planet.name;
            planetOverlay.appendChild(planetDiv);
        });
        console.log('Planet elements created, calling initial update');
        updatePlanetPositions(0, 0, 0); // Initial update
    } catch (error) {
        console.error('Error fetching planet data:', error);
        document.getElementById('orientation').innerText = 'Error fetching planet data: ' + error.message;
    }
}
</script>
<div id="orientation" style="background-color: #f0f0f0; padding: 10px;"></div>

<!-- Manual Orientation Controls -->
<div style="position: fixed; bottom: 10px; left: 10px; background: rgba(255,255,255,0.9); padding: 10px; border-radius: 8px; z-index: 1000;">
    <div style="margin-bottom: 5px;"><strong>Manual Orientation Controls</strong></div>
    <div style="margin-bottom: 5px;">
        <label>Alpha (Compass): <span id="alphaValue">0</span>°</label><br>
        <input type="range" id="alphaSlider" min="0" max="360" value="0" style="width: 200px;">
    </div>
    <div style="margin-bottom: 5px;">
        <label>Beta (Tilt): <span id="betaValue">0</span>°</label><br>
        <input type="range" id="betaSlider" min="-180" max="180" value="0" style="width: 200px;">
    </div>
    <div style="margin-bottom: 5px;">
        <label>Gamma (Roll): <span id="gammaValue">0</span>°</label><br>
        <input type="range" id="gammaSlider" min="-90" max="90" value="0" style="width: 200px;">
    </div>
</div>

<script>
// Manual orientation controls
document.getElementById('alphaSlider').addEventListener('input', function(e) {
    const alpha = parseFloat(e.target.value);
    document.getElementById('alphaValue').textContent = alpha;
    const beta = parseFloat(document.getElementById('betaSlider').value);
    const gamma = parseFloat(document.getElementById('gammaSlider').value);
    document.getElementById('orientation').innerText = `Alpha: ${alpha}, Beta: ${beta}, Gamma: ${gamma} (Manual)`;
    updatePlanetPositions(alpha, beta, gamma);
});

document.getElementById('betaSlider').addEventListener('input', function(e) {
    const beta = parseFloat(e.target.value);
    document.getElementById('betaValue').textContent = beta;
    const alpha = parseFloat(document.getElementById('alphaSlider').value);
    const gamma = parseFloat(document.getElementById('gammaSlider').value);
    document.getElementById('orientation').innerText = `Alpha: ${alpha}, Beta: ${beta}, Gamma: ${gamma} (Manual)`;
    updatePlanetPositions(alpha, beta, gamma);
});

document.getElementById('gammaSlider').addEventListener('input', function(e) {
    const gamma = parseFloat(e.target.value);
    document.getElementById('gammaValue').textContent = gamma;
    const alpha = parseFloat(document.getElementById('alphaSlider').value);
    const beta = parseFloat(document.getElementById('betaSlider').value);
    document.getElementById('orientation').innerText = `Alpha: ${alpha}, Beta: ${beta}, Gamma: ${gamma} (Manual)`;
    updatePlanetPositions(alpha, beta, gamma);
});
</script>

<video id="video" autoplay width=100% height=100%></video>
<div id="planetOverlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    <!-- Planet positions will be updated here -->
    <div id="planetData" style="display: none;"></div>
</div>

<pre id="responseData" style="background-color: #f0f0f0; padding: 10px;"></pre>
"""

# Embed the JavaScript and HTML into the Streamlit app
components.html(orientation_js, height=1600)
