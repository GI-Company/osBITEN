// This script loads the webgl-init.js file and then calls the initWebGLBackground function
document.addEventListener('DOMContentLoaded', function() {
  // Create a script element to load the webgl-init.js file
  const script = document.createElement('script');
  script.src = '../js/webgl-init.js';
  script.onload = function() {
    // Once the script is loaded, call the initWebGLBackground function
    if (typeof initWebGLBackground === 'function') {
      console.log('Calling initWebGLBackground from load-webgl.js');
      initWebGLBackground();
    } else {
      console.error('initWebGLBackground function not found');
    }
  };
  script.onerror = function() {
    console.error('Failed to load webgl-init.js');
  };
  document.head.appendChild(script);
});
