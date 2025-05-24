// WebGL Background Initialization - Fixed Version
// This file contains the fixed WebGL initialization code for the OBPI application

// Store the original initWebGLBackground function if it exists
const originalInitWebGLBackground = window.initWebGLBackground;

// Define our fixed version of the function
function fixedInitWebGLBackground() {
  try {
    // Properly declare variables with let to avoid global scope issues
    let scene = new THREE.Scene();
    let camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
    let renderer = new THREE.WebGLRenderer({
      canvas: document.getElementById('webgl-canvas'),
      antialias: true,
      alpha: true
    });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(OBPI.config.bgColor || 0x1a1a2e, 1);

    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 1.2,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.7
    });

    const starVertices = [];
    for (let i = 0; i < 15000; i++) {
      const x = THREE.MathUtils.randFloatSpread(2000);
      const y = THREE.MathUtils.randFloatSpread(2000);
      const z = THREE.MathUtils.randFloatSpread(2000);
      starVertices.push(x, y, z);
    }

    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    let stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
    camera.position.z = 1;

    // Store references in OBPI object to avoid global variables
    OBPI.webGL = {
      scene: scene,
      camera: camera,
      renderer: renderer,
      stars: stars
    };

    function animate() {
      requestAnimationFrame(animate);
      stars.rotation.x += 0.00005;
      stars.rotation.y += 0.0001;
      renderer.render(scene, camera);
    }

    animate();

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    console.log("WebGL background initialized successfully (fixed version)");
    if (OBPI.kernel && OBPI.kernel.log) {
      OBPI.kernel.log("WebGL background initialized (fixed version).", "success");
    }
  } catch (e) {
    console.error(`WebGL initialization failed: ${e.message}`);
    if (OBPI.kernel && OBPI.kernel.log) {
      OBPI.kernel.log(`WebGL initialization failed: ${e.message}`, "error");
    }
    if (OBPI.desktopElement) {
      OBPI.desktopElement.style.backgroundColor = OBPI.config.bgColor || '#1a1a2e';
    }
  }
}

// Auto-execute this script when loaded
(function() {
  // Override the global initWebGLBackground function with our fixed version
  window.initWebGLBackground = fixedInitWebGLBackground;

  // If the document is already loaded, call the function immediately
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document already loaded, calling fixed initWebGLBackground immediately');
    setTimeout(fixedInitWebGLBackground, 100); // Small delay to ensure OBPI object is fully initialized
  } else {
    // Otherwise, wait for the DOMContentLoaded event
    document.addEventListener('DOMContentLoaded', function() {
      console.log('DOMContentLoaded event fired, calling fixed initWebGLBackground');
      setTimeout(fixedInitWebGLBackground, 100); // Small delay to ensure OBPI object is fully initialized
    });
  }
})();
