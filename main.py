import streamlit as st
import json
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import requests
a=requests.get('https://api.visibleplanets.dev/v3?latitude=32&longitude=-98',verify=False)
data=dict(a.json())
# Display data
st.title("Orientation")
for obj in data['data']:
    break
    st.subheader(obj['name'])
    st.write(f"Constellation: {obj['constellation']}")
    st.write(f"Right Ascension: {obj['rightAscension']['hours']}h {obj['rightAscension']['minutes']}m {obj['rightAscension']['seconds']}s")
    st.write(f"Declination: {obj['declination']['degrees']}° {obj['declination']['arcminutes']}' {obj['declination']['arcseconds']}''")
    st.write(f"Altitude: {obj['altitude']}")
    st.write(f"Azimuth: {obj['azimuth']}")
    st.write(f"Above Horizon: {obj['aboveHorizon']}")
    st.write(f"Magnitude: {obj['magnitude']}")
    st.write(f"Naked Eye Object: {obj['nakedEyeObject']}")
    
# JavaScript to get device orientation
orientation_js = """
<script>
function getOrientation() {
    if (window.DeviceOrientationEvent) {
        window.addEventListener('deviceorientation', function(event) {
            var alpha = event.alpha.toFixed(2);
            var beta = event.beta.toFixed(2);
            var gamma = event.gamma.toFixed(2);
            document.getElementById('orientation').innerText = `Alpha: ${alpha}, Beta: ${beta}, Gamma: ${gamma}`;
        }, false);
    } else {
        document.getElementById('orientation').innerText = "Device orientation not supported.";
    }
}
getOrientation();
// Access the back camera
function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: { exact: "environment" } } })
    .then(function(stream) {
        var video = document.createElement('video');
        video.srcObject = stream;
        video.play();
        video.style.width = '100%'; // Ensure the video fits the div
        video.style.height = 'auto';
        document.getElementById('orientation').appendChild(video);
    })
    .catch(function(err) {
        console.log("Error: " + err);
        document.getElementById('orientation').innerText = "Camera not supported or permission denied.";
    });
}
startCamera();
</script>
<div id="orientation" style="width: 100%; height: 100%;"></div>;
"""

components.html(orientation_js, height=200)

components.html("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    // Set up the scene, camera, and renderer
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    var renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Create a sphere to represent the planet
    var geometry = new THREE.SphereGeometry(1, 32, 32);
    var material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    var planet = new THREE.Mesh(geometry, material);
    scene.add(planet);

    // Position the camera
    camera.position.z = 5;

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        planet.rotation.y += 0.01; // Rotate the planet
        renderer.render(scene, camera);
    }
    animate();
</script>
""")
