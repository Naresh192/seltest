
import streamlit as st
import streamlit.components.v1 as components

st.title("Orientation")

# JavaScript for Device Orientation, Camera Access, and API Call
orientation_js = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; }
        #video { display: none; }
        #container { position: relative; width: 100vw; height: 100vh; overflow: hidden; }
    </style>
</head>
<body>
    <video id="video" autoplay playsinline></video>
    <div id="container"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r146/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three/examples/js/renderers/CSS3DRenderer.js"></script>
    <script>
        // Camera feed setup
const video = document.getElementById('video');
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error('Error accessing camera:', err);
    });

// Three.js setup
const container = document.getElementById('container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.CSS3DRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

// Device orientation setup
let alpha = 0, beta = 0, gamma = 0;
if (typeof DeviceOrientationEvent !== 'undefined' && DeviceOrientationEvent.requestPermission) {
    DeviceOrientationEvent.requestPermission()
        .then(permissionState => {
            if (permissionState === 'granted') {
                window.addEventListener('deviceorientation', handleOrientation);
            }
        })
        .catch(console.error);
} else {
    window.addEventListener('deviceorientation', handleOrientation);
}

function handleOrientation(event) {
    alpha = event.alpha || 0; // Compass direction (0-360)
    beta = event.beta || 0;   // Front/back tilt (-180 to 180)
    gamma = event.gamma || 0; // Left/right tilt (-90 to 90)
}

// Planet data
const planetsData = [
    { name: 'Venus', azimuth: 45, altitude: 30, radius: 10 },
    { name: 'Mars', azimuth: 120, altitude: 20, radius: 8 },
    // Add more planets
];

// Create planet elements
const planets = planetsData.map(planet => {
    const div = document.createElement('div');
    div.className = 'planet';
    div.style.width = `${planet.radius * 2}px`;
    div.style.height = `${planet.radius * 2}px`;
    div.style.backgroundColor = 'rgba(255, 255, 0, 0.5)';
    div.style.borderRadius = '50%';
    div.textContent = planet.name;

    const cssObject = new THREE.CSS3DObject(div);
    cssObject.position.set(0, 0, 0); // Initial position
    scene.add(cssObject);
    return { ...planet, cssObject };
});

// Convert azimuth/altitude to 3D coordinates
function sphericalToCartesian(azimuth, altitude, radius) {
    const phi = THREE.MathUtils.degToRad(90 - altitude);
    const theta = THREE.MathUtils.degToRad(azimuth);
    const x = radius * Math.sin(phi) * Math.cos(theta);
    const y = radius * Math.sin(phi) * Math.sin(theta);
    const z = radius * Math.cos(phi);
    return { x, y, z };
}

// Update planet positions based on device orientation
function updatePlanets() {
    planets.forEach(planet => {
        const { x, y, z } = sphericalToCartesian(planet.azimuth, planet.altitude, 100);

        // Apply device orientation
        const euler = new THREE.Euler(
            THREE.MathUtils.degToRad(beta),  // Tilt front/back
            THREE.MathUtils.degToRad(alpha), // Compass direction
            THREE.MathUtils.degToRad(gamma), // Tilt left/right
            'YXZ' // Order of rotations
        );

        const vector = new THREE.Vector3(x, y, z);
        vector.applyEuler(euler);

        // Update planet position
        planet.cssObject.position.copy(vector);
    });
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    updatePlanets();
    renderer.render(scene, camera);
}
animate();

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
    </script>
</body>
</html>"""

# Embed the JavaScript and HTML into the Streamlit app
components.html(orientation_js, height=1600)
