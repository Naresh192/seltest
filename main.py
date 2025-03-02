import streamlit as st
import streamlit.components.v1 as components

st.title("AR Planet Finder")

orientation_js = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r127/three.min.js"></script>
<script type="module">
import { DeviceOrientationControls } from 'https://cdn.jsdelivr.net/npm/three@0.127.0/examples/jsm/controls/DeviceOrientationControls.js';

const CAMERA_FOV = 60; // Degrees, adjust based on your device's camera
let renderer, camera, scene;
let planets = [];

async function initialize() {
    // Setup Three.js scene
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(CAMERA_FOV, window.innerWidth/window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('overlay').appendChild(renderer.domElement);

    // Get device location and orientation
    const position = await getLocation();
    const orientation = await getOrientation();
    await setupCamera();
    await loadPlanets(position.coords.latitude, position.coords.longitude);
    
    animate();
}

async function getLocation() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
}

async function getOrientation() {
    return new Promise((resolve) => {
        if (typeof DeviceOrientationEvent !== 'undefined' && 
            typeof DeviceOrientationEvent.requestPermission === 'function') {
            DeviceOrientationEvent.requestPermission()
                .then(permission => {
                    if (permission === 'granted') {
                        window.addEventListener('deviceorientation', resolve);
                    }
                })
                .catch(console.error);
        } else {
            window.addEventListener('deviceorientation', resolve);
        }
    });
}

async function setupCamera() {
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

async function loadPlanets(lat, lon) {
    try {
        const response = await fetch(`https://api.visibleplanets.dev/v3?latitude=${lat}&longitude=${lon}`);
        const data = await response.json();
        
        planets = data.data.map(planet => {
            const position = sphericalToCartesian(planet.azimuth, planet.altitude);
            return {
                name: planet.name,
                position: position,
                element: createPlanetElement(planet.name)
            };
        });
    } catch (error) {
        console.error('Failed to load planets:', error);
    }
    #document.getElementById('plan')+=position;
}

function sphericalToCartesian(azimuth, altitude) {
    const phi = THREE.MathUtils.degToRad(90 - altitude);
    const theta = THREE.MathUtils.degToRad(azimuth);
    
    return new THREE.Vector3(
        Math.sin(phi) * Math.cos(theta),
        Math.cos(phi),
        Math.sin(phi) * Math.sin(theta)
    ).multiplyScalar(10);
}

function createPlanetElement(name) {
    const div = document.createElement('div');
    div.className = 'planet-marker';
    div.textContent = name;
    div.style.position = 'absolute';
    div.style.color = 'white';
    div.style.fontSize = '20px';
    div.style.textShadow = '0 0 5px black';
    document.getElementById('overlay').appendChild(div);
    return div;
}

function updatePlanetPositions() {
    const aspect = window.innerWidth / window.innerHeight;
    const fov = CAMERA_FOV;
    
    planets.forEach(planet => {
        // Update Three.js camera projection
        camera.aspect = aspect;
        camera.updateProjectionMatrix();
        
        // Get screen position
        const vector = planet.position.clone();
        vector.project(camera);
        
        // Convert normalized device coordinates to screen coordinates
        const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
        const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
        
        // Update position if visible
        if (vector.z > 0 && x > 0 && x < window.innerWidth && y > 0 && y < window.innerHeight) {
            planet.element.style.display = 'block';
            planet.element.style.left = `${x}px`;
            planet.element.style.top = `${y}px`;
        } else {
            planet.element.style.display = 'none';
        }
    });
}

function animate() {
    requestAnimationFrame(animate);
    updatePlanetPositions();
    renderer.render(scene, camera);
}

// Start the application
initialize();

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>

<style>
.planet-marker {
    transition: all 0.1s;
    transform: translate(-50%, -50%);
}
#overlay {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
}
</style>

<video id="video" autoplay playsinline style="width: 100%; height: auto;"></video>
<div id="overlay"></div>
<div id="plan"></div>
"""

components.html(orientation_js, height=800)
