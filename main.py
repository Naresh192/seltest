import streamlit as st
import streamlit.components.v1 as components

st.title("AR Planet Viewer")

orientation_js = """
<!-- ========== HTML FIRST so DOM elements exist ========== -->
<div id="statusBar" style="background:#222;color:#0f0;padding:8px 12px;font-family:monospace;font-size:13px;max-height:120px;overflow-y:auto;border-bottom:2px solid #0f0;">
  Loading...
</div>

<div style="position:relative;width:100%;height:480px;background:#1a1a2e;">
  <video id="video" autoplay playsinline muted style="width:100%;height:100%;object-fit:cover;"></video>
  <div id="planetOverlay" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;">
    <div id="planetData" style="display:none;"></div>
  </div>
</div>

<div id="orientationDisplay" style="background:#333;color:#fff;padding:6px 12px;font-family:monospace;font-size:13px;">
  Orientation: waiting...
</div>

<div style="background:#f5f5f5;padding:10px;">
  <strong>Manual Orientation Controls</strong>
  <div style="margin:4px 0;">
    <label>Alpha (Compass): <span id="alphaValue">0</span>deg</label><br>
    <input type="range" id="alphaSlider" min="0" max="360" value="0" style="width:100%;">
  </div>
  <div style="margin:4px 0;">
    <label>Beta (Tilt): <span id="betaValue">0</span>deg</label><br>
    <input type="range" id="betaSlider" min="-180" max="180" value="0" style="width:100%;">
  </div>
  <div style="margin:4px 0;">
    <label>Gamma (Roll): <span id="gammaValue">0</span>deg</label><br>
    <input type="range" id="gammaSlider" min="-90" max="90" value="0" style="width:100%;">
  </div>
</div>

<pre id="responseData" style="background:#f0f0f0;padding:10px;font-size:11px;max-height:200px;overflow:auto;display:none;"></pre>

<!-- ========== Three.js loaded BEFORE our code ========== -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r127/three.min.js"></script>

<script>
(function() {
  // --- Status logging (replaces content, never grows) ---
  var statusLines = [];
  function setStatus(msg) {
    statusLines.push(msg);
    if (statusLines.length > 6) statusLines.shift();
    document.getElementById('statusBar').innerHTML = statusLines.join('<br>');
    console.log('[AR]', msg);
  }

  setStatus('Script started');

  // Check Three.js
  if (typeof THREE === 'undefined') {
    setStatus('ERROR: Three.js failed to load');
    return;
  }
  setStatus('Three.js loaded OK');

  // --- Camera ---
  (async function startCamera() {
    try {
      var stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      document.getElementById('video').srcObject = stream;
      setStatus('Camera started');
    } catch(e) {
      setStatus('Camera error: ' + e.message);
      document.getElementById('video').style.background = '#1a1a2e';
    }
  })();

  // --- Orientation ---
  var currentAlpha = 0, currentBeta = 0, currentGamma = 0;

  function updateOrientationDisplay(a, b, g, source) {
    document.getElementById('orientationDisplay').innerText =
      'A:' + a.toFixed(1) + ' B:' + b.toFixed(1) + ' G:' + g.toFixed(1) + ' (' + source + ')';
  }

  if (window.DeviceOrientationEvent) {
    // iOS 13+ permission
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
      DeviceOrientationEvent.requestPermission().then(function(state) {
        if (state === 'granted') setStatus('Orientation permission granted');
        else setStatus('Orientation permission denied');
      }).catch(function(e) { setStatus('Orientation permission error'); });
    }
    window.addEventListener('deviceorientation', function(e) {
      if (e.alpha !== null || e.beta !== null || e.gamma !== null) {
        currentAlpha = e.alpha || 0;
        currentBeta = e.beta || 0;
        currentGamma = e.gamma || 0;
        updateOrientationDisplay(currentAlpha, currentBeta, currentGamma, 'Device');
        document.getElementById('alphaSlider').value = currentAlpha;
        document.getElementById('betaSlider').value = currentBeta;
        document.getElementById('gammaSlider').value = currentGamma;
        document.getElementById('alphaValue').textContent = currentAlpha.toFixed(0);
        document.getElementById('betaValue').textContent = currentBeta.toFixed(0);
        document.getElementById('gammaValue').textContent = currentGamma.toFixed(0);
        updatePlanetPositions(currentAlpha, currentBeta, currentGamma);
      }
    }, false);
  }
  setTimeout(function() { setStatus('Orientation: ' + (currentAlpha || currentBeta || currentGamma ? 'active' : 'no sensor, use sliders')); }, 2000);

  // --- Manual sliders ---
  function onSliderChange() {
    var a = parseFloat(document.getElementById('alphaSlider').value);
    var b = parseFloat(document.getElementById('betaSlider').value);
    var g = parseFloat(document.getElementById('gammaSlider').value);
    document.getElementById('alphaValue').textContent = a;
    document.getElementById('betaValue').textContent = b;
    document.getElementById('gammaValue').textContent = g;
    updateOrientationDisplay(a, b, g, 'Manual');
    updatePlanetPositions(a, b, g);
  }
  document.getElementById('alphaSlider').addEventListener('input', onSliderChange);
  document.getElementById('betaSlider').addEventListener('input', onSliderChange);
  document.getElementById('gammaSlider').addEventListener('input', onSliderChange);

  // --- Screen position calculation ---
  function getScreenPosition(azimuth, altitude, alpha, beta, gamma, hFov, vFov) {
    var azRad = THREE.MathUtils.degToRad(azimuth);
    var altRad = THREE.MathUtils.degToRad(altitude);
    var x = Math.cos(altRad) * Math.sin(azRad);
    var y = Math.sin(altRad);
    var z = Math.cos(altRad) * Math.cos(azRad);
    var pos = new THREE.Vector3(x, y, z);

    var euler = new THREE.Euler(
      THREE.MathUtils.degToRad(beta),
      THREE.MathUtils.degToRad(alpha),
      THREE.MathUtils.degToRad(gamma),
      'YXZ'
    );
    pos.applyEuler(euler);

    if (pos.z <= 0.01) return null; // behind camera

    var hFovRad = THREE.MathUtils.degToRad(hFov);
    var vFovRad = THREE.MathUtils.degToRad(vFov);
    var sx = (pos.x / pos.z) / Math.tan(hFovRad / 2);
    var sy = (pos.y / pos.z) / Math.tan(vFovRad / 2);

    var px = (sx * 0.5 + 0.5) * 100;
    var py = (0.5 - sy * 0.5) * 100;

    if (px < -20 || px > 120 || py < -20 || py > 120) return null;
    return { x: px, y: py };
  }

  // --- Update planet positions ---
  function updatePlanetPositions(alpha, beta, gamma) {
    var el = document.getElementById('planetData');
    if (!el || !el.innerText) return;
    var planets = JSON.parse(el.innerText);
    planets.forEach(function(p) {
      var pos = getScreenPosition(p.azimuth, p.altitude, alpha, beta, gamma, 70, 56);
      var div = document.getElementById('planet_' + p.name);
      if (!div) return;
      if (pos) {
        div.style.left = pos.x + '%';
        div.style.top = pos.y + '%';
        div.style.display = 'block';
      } else {
        div.style.display = 'none';
      }
    });
  }

  // --- Create planet elements ---
  function createPlanetElements(planets) {
    var overlay = document.getElementById('planetOverlay');
    if (!overlay) { setStatus('ERROR: planetOverlay not found'); return; }

    // Keep planetData div, clear the rest
    var dataDiv = document.getElementById('planetData');
    overlay.innerHTML = '';
    overlay.appendChild(dataDiv);

    var info = [];
    planets.forEach(function(p, i) {
      var div = document.createElement('div');
      div.id = 'planet_' + p.name;
      div.style.cssText = 'position:absolute;color:#fff;font-size:16px;font-weight:bold;' +
        'text-shadow:1px 1px 3px #000;padding:6px 10px;background:rgba(255,0,0,0.7);' +
        'border-radius:6px;border:2px solid yellow;z-index:100;pointer-events:none;' +
        'left:50%;top:50%;display:block;transform:translate(-50%,-50%);';
      div.textContent = p.name;
      overlay.appendChild(div);
      info.push((i+1) + '. ' + p.name + ' Az:' + p.azimuth.toFixed(1) + ' Alt:' + p.altitude.toFixed(1));
    });
    setStatus('Created ' + planets.length + ' planets: ' + info.join(', '));
  }

  // --- Fetch planet data ---
  async function fetchPlanetData(lat, lon) {
    setStatus('Fetching planets for ' + lat.toFixed(2) + ', ' + lon.toFixed(2));
    try {
      var resp = await fetch('https://api.visibleplanets.dev/v3?latitude=' + lat + '&longitude=' + lon);
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      var data = await resp.json();
      if (!data.data || data.data.length === 0) throw new Error('No planets returned');
      setStatus('API returned ' + data.data.length + ' planets');

      // Fetch radius for each planet
      for (var i = 0; i < data.data.length; i++) {
        try {
          var br = await fetch('https://api.le-systeme-solaire.net/rest/bodies/' + data.data[i].name.toLowerCase());
          var bd = await br.json();
          data.data[i].meanradius = bd.meanRadius || 0;
        } catch(e) { data.data[i].meanradius = 0; }
      }

      document.getElementById('planetData').innerText = JSON.stringify(data.data);
      document.getElementById('responseData').innerText = JSON.stringify(data, null, 2);
      createPlanetElements(data.data);
      updatePlanetPositions(0, 0, 0);
    } catch(e) {
      setStatus('API error: ' + e.message + ' - using fallback');
      var fallback = [
        { name: 'Venus', azimuth: 45, altitude: 30, meanradius: 6051 },
        { name: 'Mars', azimuth: 120, altitude: 20, meanradius: 3389 },
        { name: 'Jupiter', azimuth: 200, altitude: 45, meanradius: 69911 },
        { name: 'Saturn', azimuth: 280, altitude: 15, meanradius: 58232 }
      ];
      document.getElementById('planetData').innerText = JSON.stringify(fallback);
      createPlanetElements(fallback);
      updatePlanetPositions(0, 0, 0);
    }
  }

  // --- Get location and start ---
  setStatus('Requesting location...');
  navigator.geolocation.getCurrentPosition(
    function(pos) {
      setStatus('Location: ' + pos.coords.latitude.toFixed(4) + ', ' + pos.coords.longitude.toFixed(4));
      fetchPlanetData(pos.coords.latitude, pos.coords.longitude);
    },
    function(err) {
      setStatus('Location error: ' + err.message + ' - using New York');
      fetchPlanetData(40.7128, -74.0060);
    }
  );
})();
</script>
"""

components.html(orientation_js, height=800)
