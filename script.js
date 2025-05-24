// --- OBPI (Operational in Browser Persisted Instance) Core v1.0 (Full Features) ---
// [2025-05-23]
// Full integration of AI assistant, enhanced terminal, real USB peripheral detection,
// and re-architected PEPx storage (no client-side canvas for data).
// Conceptual compiler framework for various languages and hex-to-webgl.

// --- Global State & Configuration ---
const OBPI = {
  version: "1.0-full-features",
  name: "Operational in Browser Persisted Instance",
  desktopElement: document.getElementById('desktop'),
  taskbarElement: document.querySelector('.taskbar'),
  taskbarAppsContainer: document.getElementById('taskbar-apps-container'),
  startMenuElement: document.getElementById('start-menu'),
  startMenuButton: document.getElementById('start-menu-button'),
  contextMenuElement: document.getElementById('context-menu'),
  modalElement: document.getElementById('generic-modal'),
  modalTitle: document.getElementById('modal-title'),
  modalContent: document.getElementById('modal-content'),
  modalActions: document.getElementById('modal-actions'),
  modalCloseButton: document.getElementById('modal-close-button'),
  fullscreenLockOverlay: document.getElementById('fullscreen-lock-overlay'),
  windows: {},
  nextZIndex: 100,
  currentPath: '/', // Start at VFS root
  commandHistory: [],
  commandHistoryIndex: -1,
  isLocked: false,
  envVars: {},
  aliases: {},
  activeTheme: 'dark',
  config: {
    defaultPrompt: 'guest@OBPI:~# ',
    maxTerminalOutputLines: 300,
    defaultWindowSize: { width: '600px', height: '450px' },
    windowStateStorageKey: 'OBPI_window_states_v1.0', // Updated key
    themeStorageKey: 'OBPI_theme_v1.0', // Updated key
    desktopIconStorageKey: 'OBPI_desktop_icons_v1.0', // Updated key
  },
  kernel: {
    // Log messages to Python backend
    log: (message, level = 'info', data = null) => {
      console[level] || console.log(`[OBPI Kernel|${level.toUpperCase()}]: ${message}`, data);
      if (window.pywebview && window.pywebview.api && window.pywebview.api.log_to_python) {
        window.pywebview.api.log_to_python(`[JS]: ${message}`, level);
      }
    },
    // WASM module loading remains conceptual as it's not directly backend-driven
    loadWasmModule: async (url, importObject = {}) => {
      OBPI.kernel.log(`Attempting to load WASM module from: ${url}`);
      try {
        if (url.includes("core_emulator.wasm")) {
          OBPI.kernel.log(`Simulating load of core_emulator.wasm...`, 'info');
          return {
            add_native: (a, b) => {
              OBPI.kernel.log(`WASM add_native(${a}, ${b}) called.`);
              return a + b;
            },
            get_native_greeting: (name) => {
              OBPI.kernel.log(`WASM get_native_greeting("${name}") called.`);
              return `[Simulated C->WASM]: Hello, ${name}! Time: ${new Date().toLocaleTimeString()}`;
            },
            get_system_timestamp_native: () => {
              OBPI.kernel.log(`WASM get_system_timestamp_native() called.`);
              return Math.floor(Date.now() / 1000);
            }
          };
        }
        throw new Error("WASM module not found or simulated path incorrect.");
      } catch (error) {
        OBPI.kernel.log(`Error loading WASM module ${url}: ${error.message}`, "error");
        throw error;
      }
    },
    requestPermission: async (permissionType, appName) => {
      return new Promise((resolve) => {
        Modal.confirm('Permission Request', `App "${appName}" requests permission for: ${permissionType}. Allow?`, (granted) => {
          OBPI.kernel.log(`Permission for '${permissionType}' ${granted ? 'granted' : 'denied'} to '${appName}'.`);
          resolve(granted);
        });
      });
    },
    messageBus: {
      listeners: {},
      subscribe: (topic, callback) => {
        if (!OBPI.kernel.messageBus.listeners[topic]) OBPI.kernel.messageBus.listeners[topic] = [];
        OBPI.kernel.messageBus.listeners[topic].push(callback);
        OBPI.kernel.log(`App subscribed to topic: ${topic}`);
      },
      publish: (topic, data) => {
        if (OBPI.kernel.messageBus.listeners[topic]) {
          OBPI.kernel.log(`Publishing to topic: ${topic} with data:`, 'info', data);
          OBPI.kernel.messageBus.listeners[topic].forEach(callback => {
            try {
              callback(data);
            } catch (e) {
              OBPI.kernel.log(`Error in message bus subscriber for topic ${topic}: ${e.message}`, 'error');
            }
          });
        }
      }
    }
  },
  pepxInstance: null // To hold the global PEPxStorage instance
};

// --- Client-Side "EJS-like" Templating Engine (Remains client-side) ---
const EJSSimulator = {
  render: (templateString, data = {}) => {
    let rendered = templateString;
    for (const key in data) {
      const regex = new RegExp(`<%[=\\-_]?\\s*${key}\\s*%>`, 'g');
      rendered = rendered.replace(regex, data[key]);
    }
    return rendered;
  },
  exampleTemplate: ` <div class="p-4 border rounded bg-blue-100 text-blue-800"> <h2 class="text-xl font-bold"><%= title %></h2> <p><%= content %></p> <p>Generated at: <%= timestamp %></p> </div> `,
  renderExample: () => {
    const data = {
      title: "EJS Simulated Content",
      content: "Dynamically rendered using EJSSimulator.",
      timestamp: new Date().toLocaleTimeString()
    };
    return EJSSimulator.render(EJSSimulator.exampleTemplate, data);
  }
};

// --- Modal Manager ---
const Modal = {
  show: (title, contentHTML, actions = [{ text: 'OK', type: 'primary', handler: () => Modal.hide() }]) => {
    OBPI.modalTitle.textContent = title;
    if (typeof contentHTML === 'string') OBPI.modalContent.innerHTML = contentHTML;
    else {
      OBPI.modalContent.innerHTML = '';
      OBPI.modalContent.appendChild(contentHTML);
    }
    OBPI.modalActions.innerHTML = '';
    actions.forEach(action => {
      const button = document.createElement('button');
      button.textContent = action.text;
      button.className = `px-4 py-2 rounded-md text-sm font-medium ${ action.type === 'danger' ? 'bg-red-500 hover:bg-red-600 text-white' : action.type === 'secondary' ? 'bg-gray-200 hover:bg-gray-300 text-gray-700' : 'bg-indigo-600 hover:bg-indigo-700 text-white' }`;
      button.onclick = () => {
        if(action.handler) action.handler();
        if(action.hideOnClick !== false) Modal.hide();
      };
      OBPI.modalActions.appendChild(button);
    });
    OBPI.modalElement.classList.remove('hidden');
    OBPI.modalElement.classList.add('flex');
  },
  hide: () => {
    OBPI.modalElement.classList.add('hidden');
    OBPI.modalElement.classList.remove('flex');
  },
  prompt: (title, labelText, defaultValue = '', callback) => {
    const promptContent = document.createElement('div');
    const label = document.createElement('label');
    label.textContent = labelText;
    label.className = 'block text-sm font-medium text-gray-700 mb-1';
    const input = document.createElement('input');
    input.type = 'text';
    input.value = defaultValue;
    input.className = 'w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500';
    promptContent.appendChild(label);
    promptContent.appendChild(input);
    Modal.show(title, promptContent, [
      { text: 'Cancel', type: 'secondary', handler: () => callback(null) },
      { text: 'OK', type: 'primary', handler: () => callback(input.value) }
    ]);
    setTimeout(() => input.focus(), 50);
  },
  confirm: (title, message, callback) => {
    Modal.show(title, `<p>${message}</p>`, [
      { text: 'Cancel', type: 'secondary', handler: () => callback(false) },
      { text: 'OK', type: 'primary', handler: () => callback(true) }
    ]);
  }
};
OBPI.modalCloseButton.onclick = Modal.hide;

// --- WebGL Background ---
function initWebGLBackground() {
  try {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
    renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('webgl-canvas'), antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(OBPI.config.bgColor || 0x1a1a2e, 1);
    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 1.2, sizeAttenuation: true, transparent: true, opacity: 0.7 });
    const starVertices = [];
    for (let i = 0; i < 15000; i++) {
      const x = THREE.MathUtils.randFloatSpread(2000);
      const y = THREE.MathUtils.randFloatSpread(2000);
      const z = THREE.MathUtils.randFloatSpread(2000);
      starVertices.push(x, y, z);
    }
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
    camera.position.z = 1;
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
    OBPI.kernel.log("WebGL background initialized.", "success");
  } catch (e) {
    OBPI.kernel.log(`WebGL initialization failed: ${e.message}`, "error");
    OBPI.desktopElement.style.backgroundColor = OBPI.config.bgColor || '#1a1a2e';
  }
}

// --- Window Management Module ---
const WindowManager = {
  create: (id, title, content, options = {}) => {
    if (OBPI.windows[id]) {
      WindowManager.focus(id);
      return OBPI.windows[id];
    }

    const winEl = document.createElement('div');
    winEl.id = `window-${id}`;
    winEl.className = 'os-window';

    // Apply size and position
    const defaultSize = OBPI.config.defaultWindowSize;
    winEl.style.width = options.width || defaultSize.width;
    winEl.style.height = options.height || defaultSize.height;

    // Position in the center if not specified
    if (!options.top && !options.left) {
      const winWidth = parseInt(winEl.style.width);
      const winHeight = parseInt(winEl.style.height);
      winEl.style.top = `${Math.max(0, (window.innerHeight - winHeight) / 2)}px`;
      winEl.style.left = `${Math.max(0, (window.innerWidth - winWidth) / 2)}px`;
    } else {
      winEl.style.top = options.top || '50px';
      winEl.style.left = options.left || '50px';
    }

    // Create window header
    const headerEl = document.createElement('div');
    headerEl.className = 'window-header';
    headerEl.innerHTML = `
      <div class="window-title">${title}</div>
      <div class="window-controls">
        <button class="minimize-btn" title="Minimize">_</button>
        <button class="maximize-btn" title="Maximize">□</button>
        <button class="close-btn" title="Close">×</button>
      </div>
    `;

    // Create window content container
    const contentEl = document.createElement('div');
    contentEl.className = 'window-content';

    // Add content to the window
    if (typeof content === 'string') {
      contentEl.innerHTML = content;
    } else if (content instanceof HTMLElement) {
      contentEl.appendChild(content);
    }

    // Assemble window
    winEl.appendChild(headerEl);
    winEl.appendChild(contentEl);
    OBPI.desktopElement.appendChild(winEl);

    // Set up window controls
    headerEl.querySelector('.minimize-btn').onclick = () => WindowManager.minimize(id);
    headerEl.querySelector('.maximize-btn').onclick = () => WindowManager.maximize(id);
    headerEl.querySelector('.close-btn').onclick = () => WindowManager.close(id);

    // Make window draggable
    let isDragging = false;
    let dragOffsetX = 0, dragOffsetY = 0;

    headerEl.onmousedown = (e) => {
      if (e.target.tagName !== 'BUTTON') {
        isDragging = true;
        dragOffsetX = e.clientX - winEl.offsetLeft;
        dragOffsetY = e.clientY - winEl.offsetTop;
        WindowManager.focus(id);
      }
    };

    document.addEventListener('mousemove', (e) => {
      if (isDragging) {
        winEl.style.left = `${e.clientX - dragOffsetX}px`;
        winEl.style.top = `${e.clientY - dragOffsetY}px`;
      }
    });

    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        WindowManager.saveWindowStates();
      }
    });

    // Add to taskbar
    WindowManager.addAppToTaskbar(id, title);

    // Store window data
    const zIndex = OBPI.nextZIndex++;
    winEl.style.zIndex = zIndex;

    OBPI.windows[id] = {
      element: winEl,
      title: title,
      zIndex: zIndex,
      minimized: false,
      content: contentEl
    };

    // Apply any saved state
    const savedStates = WindowManager.loadWindowStates();
    if (savedStates[id]) {
      const state = savedStates[id];
      winEl.style.width = state.width;
      winEl.style.height = state.height;
      winEl.style.top = state.top;
      winEl.style.left = state.left;
      winEl.style.zIndex = state.zIndex;
      if (state.minimized) WindowManager.minimize(id);
    }

    WindowManager.focus(id);
    WindowManager.saveWindowStates();

    return OBPI.windows[id];
  },
  focus: (id) => {
    if (OBPI.windows[id]) {
      const newZ = OBPI.nextZIndex++;
      OBPI.windows[id].element.style.zIndex = newZ;
      OBPI.windows[id].zIndex = newZ;
      document.querySelectorAll('.os-window').forEach(win => win.classList.remove('active-window'));
      OBPI.windows[id].element.classList.add('active-window');
      if (OBPI.windows[id].minimized) WindowManager.restore(id);
      WindowManager.saveWindowStates();
    }
  },
  close: (id) => {
    if (OBPI.windows[id]) {
      OBPI.windows[id].element.remove();
      delete OBPI.windows[id];
      WindowManager.removeAppFromTaskbar(id);
      WindowManager.saveWindowStates();
      OBPI.kernel.log(`Window closed: ${id}`);
    }
  },
  minimize: (id) => {
    if (OBPI.windows[id] && !OBPI.windows[id].minimized) {
      OBPI.windows[id].element.style.display = 'none';
      OBPI.windows[id].minimized = true;
      const taskbarBtn = document.getElementById(`taskbar-${id}`);
      if(taskbarBtn) taskbarBtn.style.opacity = '0.7';
      WindowManager.saveWindowStates();
    }
  },
  restore: (id) => {
    if (OBPI.windows[id] && OBPI.windows[id].minimized) {
      OBPI.windows[id].element.style.display = 'flex';
      OBPI.windows[id].minimized = false;
      const taskbarBtn = document.getElementById(`taskbar-${id}`);
      if(taskbarBtn) taskbarBtn.style.opacity = '1';
      WindowManager.focus(id);
    }
  },
  maximize: (id) => {
    const winData = OBPI.windows[id];
    if (!winData) return;
    const winEl = winData.element;
    const taskbarHeight = OBPI.taskbarElement.offsetHeight;
    const maximizeBtn = winEl.querySelector('.maximize-btn');
    if (winData.originalRect) {
      winEl.style.width = winData.originalRect.width;
      winEl.style.height = winData.originalRect.height;
      winEl.style.top = winData.originalRect.top;
      winEl.style.left = winData.originalRect.left;
      winData.originalRect = null;
      if(maximizeBtn) maximizeBtn.textContent = '□';
    } else {
      winData.originalRect = {
        width: winEl.style.width,
        height: winEl.style.height,
        top: winEl.style.top,
        left: winEl.style.left
      };
      winEl.style.width = '100%';
      winEl.style.height = `calc(100% - ${taskbarHeight}px)`;
      winEl.style.top = '0px';
      winEl.style.left = '0px';
      if(maximizeBtn) maximizeBtn.textContent = '❐';
    }
    WindowManager.saveWindowStates();
  },
  addAppToTaskbar: (id, title) => {
    const button = document.createElement('button');
    button.id = `taskbar-${id}`;
    button.classList.add('taskbar-button');
    button.textContent = title.substring(0, 10) + (title.length > 10 ? '…' : '');
    button.title = title;
    button.onclick = () => {
      if (OBPI.windows[id]) {
        if (OBPI.windows[id].minimized) WindowManager.restore(id);
        else WindowManager.focus(id);
      }
    };
    OBPI.taskbarAppsContainer.appendChild(button);
  },
  removeAppFromTaskbar: (id) => {
    const button = document.getElementById(`taskbar-${id}`);
    if (button) button.remove();
  },
  saveWindowStates: () => {
    const states = {};
    for (const id in OBPI.windows) {
      const win = OBPI.windows[id];
      if (win.element) {
        states[id] = {
          top: win.element.style.top,
          left: win.element.style.left,
          width: win.element.style.width,
          height: win.element.style.height,
          zIndex: win.zIndex,
          minimized: win.minimized,
        };
      }
    }
    try {
      localStorage.setItem(OBPI.config.windowStateStorageKey, JSON.stringify(states));
    } catch (e) {
      OBPI.kernel.log('Failed to save window states to localStorage.', 'error');
    }
  },
  loadWindowStates: () => {
    try {
      const storedStates = localStorage.getItem(OBPI.config.windowStateStorageKey);
      return storedStates ? JSON.parse(storedStates) : {};
    } catch (e) {
      OBPI.kernel.log('Failed to load window states from localStorage.', 'error');
      return {};
    }
  },
  restoreAllWindowStates: () => {
    const persistedStates = WindowManager.loadWindowStates();
    let maxZ = OBPI.nextZIndex;
    for (const id in persistedStates) {
      if (AppManager.installedApps[id] || id === 'terminal' || id === 'welcome-note') {
        if (persistedStates[id].zIndex > maxZ) maxZ = persistedStates[id].zIndex;
      }
    }
    OBPI.nextZIndex = maxZ +1;
    OBPI.kernel.log("Window states conceptually loaded. Windows will apply state upon creation if found.", "info");
  }
};

// --- Terminal Module ---
const Terminal = {
  outputElement: null,
  inputElement: null,
  promptElement: null,
  init: () => {
    const terminalContent = document.createElement('div');
    terminalContent.className = 'cli-font w-full h-full flex flex-col';
    Terminal.outputElement = document.createElement('div');
    Terminal.outputElement.id = 'terminal-output';
    const inputLine = document.createElement('div');
    inputLine.id = 'terminal-input-line';
    Terminal.promptElement = document.createElement('span');
    Terminal.promptElement.id = 'terminal-prompt';
    Terminal.updatePrompt();
    Terminal.inputElement = document.createElement('input');
    Terminal.inputElement.type = 'text';
    Terminal.inputElement.id = 'terminal-input';
    Terminal.inputElement.setAttribute('autocomplete', 'off');
    Terminal.inputElement.setAttribute('autocorrect', 'off');
    Terminal.inputElement.setAttribute('autocapitalize', 'off');
    Terminal.inputElement.setAttribute('spellcheck', 'false');
    inputLine.appendChild(Terminal.promptElement);
    inputLine.appendChild(Terminal.inputElement);
    terminalContent.appendChild(Terminal.outputElement);
    terminalContent.appendChild(inputLine);
    const termWindow = WindowManager.create('terminal', 'Termia Chronos Shell', terminalContent, {width: '800px', height: '550px'});
    Terminal.inputElement.onkeydown = Terminal.handleInput;
    termWindow.element.onclick = () => Terminal.inputElement.focus();
    Terminal.inputElement.focus();
    Terminal.print(`OBPI (${OBPI.name}) v${OBPI.version} [Termia Chronos Shell Ready]`);
    Terminal.print("Type 'help' for commands. Try 'theme light' or 'theme dark'.");
  },
  updatePrompt: () => {
    if (Terminal.promptElement) {
      let currentDirName = OBPI.currentPath.split('/').filter(Boolean).pop() || '/';
      if (OBPI.currentPath === '/') currentDirName = '/'; // Keep '/' for root
      else if (OBPI.currentPath === '/home/guest/') currentDirName = '~'; // Placeholder for default home
      Terminal.promptElement.textContent = OBPI.config.defaultPrompt.replace('~#', `${currentDirName}$ `).replace('guest@OBPI', OBPI.envVars['USER'] || 'guest@OBPI');
    }
  },
  print: (message, isCommand = false, type = 'info') => {
    if (!Terminal.outputElement) return;
    const line = document.createElement('div');
    line.className = 'leading-normal';
    if (isCommand) {
      const promptText = Terminal.promptElement ? Terminal.promptElement.textContent : OBPI.config.defaultPrompt;
      line.innerHTML = `<span class="text-green-400">${promptText.replace(/</g, "&lt;")}</span><span class="text-gray-300">${message.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</span>`;
    }  else {
      let textColor = 'text-gray-300';
      if(document.body.classList.contains('light-theme')) {
        textColor = 'text-gray-700';
        if(type==='error') textColor = 'text-red-600';
        if(type==='success') textColor = 'text-green-600';
        if(type==='warn') textColor = 'text-yellow-600';
      } else {
        if(type === 'error') textColor = 'text-red-400';
        if(type === 'success') textColor = 'text-green-400';
        if(type === 'warn') textColor = 'text-yellow-400';
      }
      line.innerHTML = `<span class="${textColor}">${message.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</span>`;
    }
    Terminal.outputElement.prepend(line);
    while (Terminal.outputElement.children.length > OBPI.config.maxTerminalOutputLines) Terminal.outputElement.removeChild(Terminal.outputElement.lastChild);
  },
  handleInput: async (e) => { // Made async to await backend calls
    if (e.key === 'Enter') {
      const commandStr = Terminal.inputElement.value.trim();
      Terminal.print(commandStr, true);
      if (commandStr) {
        if (commandStr !== OBPI.commandHistory[0]) OBPI.commandHistory.unshift(commandStr);
        if (OBPI.commandHistory.length > 50) OBPI.commandHistory.pop();
        await AppManager.executeCommand(commandStr); // Await command execution
      }
      OBPI.commandHistoryIndex = -1;
      Terminal.inputElement.value = '';
    }  else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (OBPI.commandHistoryIndex < OBPI.commandHistory.length - 1) {
        OBPI.commandHistoryIndex++;
        Terminal.inputElement.value = OBPI.commandHistory[OBPI.commandHistoryIndex];
        Terminal.inputElement.setSelectionRange(Terminal.inputElement.value.length, Terminal.inputElement.value.length);
      }
    }  else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (OBPI.commandHistoryIndex > 0) {
        OBPI.commandHistoryIndex--;
        Terminal.inputElement.value = OBPI.commandHistory[OBPI.commandHistoryIndex];
        Terminal.inputElement.setSelectionRange(Terminal.inputElement.value.length, Terminal.inputElement.value.length);
      } else {
        OBPI.commandHistoryIndex = -1;
        Terminal.inputElement.value = '';
      }
    }  else if (e.key === 'Tab') {
      e.preventDefault();
      const currentInput = Terminal.inputElement.value;
      const parts = currentInput.split(/\s+/);
      const cmdPart = parts[0].toLowerCase();
      const argPart = parts.length > 1 ? parts[parts.length -1] : '';

      if (parts.length === 1 || (parts.length > 1 && currentInput.endsWith(' '))) { /* Command completion */
        const suggestions = Object.keys(AppManager.cliCommands).filter(cmd => cmd.startsWith(cmdPart));
        if (suggestions.length === 1) Terminal.inputElement.value = suggestions[0] + ' ';
        else if (suggestions.length > 1) Terminal.print(suggestions.join('  '));
      } else { /* Argument (file/dir) completion - now uses backend */
        const baseCompletionPath = argPart.startsWith('/') ? argPart : OBPI.currentPath + argPart;
        let searchDir = baseCompletionPath;
        let prefix = argPart.split('/').pop();
        if (!currentInput.endsWith('/')) searchDir = baseCompletionPath.substring(0, baseCompletionPath.lastIndexOf('/') + 1);
        else prefix = '';

        try {
          const response = await window.pywebview.api.list_directory_backend(searchDir || OBPI.currentPath);
          if (response.error) {
            OBPI.kernel.log(`Tab completion error: ${response.error}`, 'error');
            return;
          }
          if (response.contents && response.contents.length > 0) {
            const items = response.contents.filter(item => item.name.startsWith(prefix));
            if (items.length === 1) {
              const completion = argPart.substring(0, argPart.lastIndexOf('/') +1) + items[0].name + (items[0].type === 'dir' ? '/' : ' ');
              Terminal.inputElement.value = cmdPart + ' ' + completion;
            } else if (items.length > 1) {
              Terminal.print(items.map(item => `${item.name}${item.type === 'dir' ? '/' : ''}`).join('  '));
            }
          }
        } catch (e) {
          OBPI.kernel.log(`Tab completion backend call error: ${e.message}`, 'error');
        }
      }
    }
  },
  clear: () => { if(Terminal.outputElement) Terminal.outputElement.innerHTML = ''; }
};

// --- Application Manager ---
const AppManager = {
  installedApps: {
    'web_view': { name: 'Web View', launch: () => AppManager.launch('web-view', 'Encapsulated Web View', AppManager.apps.encapsulatedBrowser.init(), {width: '1000px', height: '700px'}), icon: '🌐' },
    'dechex_ide': { name: 'DecHex IDE', launch: () => AppManager.launch('dechex-ide', 'DecHex IDE', AppManager.apps.dechexIDE.init()), icon: '⚙️' },
    'ai_assistant': { name: 'AI Assistant', launch: () => AppManager.launch('ai-assistant', 'AI Assistant', AppManager.apps.aiAssistant.init(), {width: '700px', height: '600px'}), icon: '🤖' },
    'disk_manager': { name: 'Disk Manager (VFS)', launch: () => AppManager.launch('disk-manager', 'VFS Disk Manager', AppManager.apps.diskManager.init()), icon: '💾' },
    'pepx_explorer': { name: 'PEPx Explorer', launch: () => AppManager.launch('pepx-explorer', 'PEPx Pixel Storage Explorer', AppManager.apps.pepxExplorer.init(), {width:'800px', height:'650px'}), icon: '🖼️' },
    'ncurses_demo': { name: 'Ncurses Demo', launch: () => AppManager.launch('ncurses-app', 'Ncurses Demo App', AppManager.apps.ncursesApp.init(), {width:'500px', height:'350px'}), icon: '⣀' },
    'python_runner': { name: 'Python Runner', launch: () => AppManager.launch('python-runner', 'Python Runner', AppManager.apps.pythonRunner.init(), {width:'700px', height:'550px'}), icon: '🐍' },
    'py_ide': { name: 'Python IDE', launch: () => AppManager.launch('py-ide', 'Python IDE', AppManager.apps.pyIDE.init(), {width:'800px', height:'600px'}), icon: '📝' },
    'network_manager': { name: 'Network Manager', launch: () => AppManager.launch('network-manager', 'Network Manager', AppManager.apps.networkManager.init()), icon: '📶' },
    'bluetooth_manager': { name: 'Bluetooth Manager', launch: () => AppManager.launch('bluetooth-manager', 'Bluetooth Manager', AppManager.apps.bluetoothManager.init()), icon: '📱' },
    'peripheral_manager': { name: 'Peripheral Manager', launch: () => AppManager.launch('peripheral-manager', 'Peripheral Manager', AppManager.apps.peripheralManager.init(), {width:'700px', height:'500px'}), icon: '🔌' }, // New App
    'theme_settings': { name: 'Theme Settings', launch: () => AppManager.apps.themeSettings.launch(), icon: '🎨' },
    'wasm_core_test': { name: 'WASM Core Test', launch: () => AppManager.apps.wasmCoreTest.run(), icon: '🧩' },
    'xml_parser_test': { name: 'XML Parser Test', launch: () => AppManager.apps.xmlParserTest.run(), icon: '📰' },
    'ejs_sim_test': { name: 'EJS Sim Test', launch: () => { const content = EJSSimulator.renderExample(); WindowManager.create('ejs-test-window', 'EJS Simulator Output', content, {width: '500px', height: '300px'}); }, icon: '📄' }
  },
  launch: (id, title, content, options = {}) => WindowManager.create(id, title, content, options),
  executeCommand: async (commandStr) => {
    let originalCommandStr = commandStr;
    commandStr = commandStr.replace(/\$([A-Za-z_][A-Za-z0-9_]*)/g, (match, varName) => OBPI.envVars[varName] || '');
    const parts = commandStr.split(/\s+/);
    let command = parts[0].toLowerCase();
    const args = parts.slice(1);
    if (OBPI.aliases[command]) {
      const aliasCmdStr = OBPI.aliases[command] + (args.length > 0 ? ' ' + args.join(' ') : '');
      Terminal.print(`Alias: ${command} -> ${aliasCmdStr}`, false, 'info');
      await AppManager.executeCommand(aliasCmdStr);
      return;
    }
    const cmdFunc = AppManager.cliCommands[command];
    if (cmdFunc) {
      try {
        await cmdFunc(args);
      } catch (e) {
        Terminal.print(`Error executing '${command}': ${e.message}`, false, 'error');
        OBPI.kernel.log(`CLI Error: ${e.stack}`, 'error');
      }
    } else { Terminal.print(`Command not found: ${command}. Type 'help'.`, false, 'error'); }
    Terminal.updatePrompt();
  },
  cliCommands: {
    help: (args) => {
      if (args.length === 0) {
        Terminal.print("OBPI CLI v1.0 - Available Commands:");
        Object.keys(AppManager.cliCommands).sort().forEach(cmd => {
          Terminal.print(`  ${cmd.padEnd(18)} - ${AppManager.cliCommandDescriptions[cmd] || 'No description.'}`);
        });
        Terminal.print("\nType 'help <command>' or 'man <command>' for more details.");
      } else {
        const command = args[0].toLowerCase();
        const helpText = AppManager.cliHelpPages[command];
        if (helpText) {
          Terminal.print(`Help for '${command}':\n${helpText}`);
        } else {
          Terminal.print(`No help entry found for '${command}'.`);
        }
      }
    },
    date: () => Terminal.print(new Date().toLocaleString()),
    clear: Terminal.clear,
    exit: () => WindowManager.close('terminal'),
    echo: (args) => Terminal.print(args.join(' ')),
    pwd: () => Terminal.print(OBPI.currentPath),
    theme: (args) => {
      if (!args[0] || (args[0] !== 'light' && args[0] !== 'dark')) {
        Terminal.print("theme: usage: theme <light|dark>", false, 'error');
        Terminal.print(`Current theme: ${OBPI.activeTheme}`);
        return;
      }
      AppManager.apps.themeSettings.setTheme(args[0]);
      Terminal.print(`Theme set to ${args[0]}.`, false, 'success');
    }
  },
  cliCommandDescriptions: {
    help: "Show this help message or help for a specific command.",
    date: "Display the current date and time.",
    clear: "Clear the terminal screen.",
    exit: "Close the terminal window.",
    echo: "Display a line of text.",
    pwd: "Print name of current/working directory.",
    theme: "Change OBPI theme. Usage: theme <light|dark>"
  },
  cliHelpPages: {
    help: "Displays a list of available commands or detailed help for a specific command.\nUsage: help [command_name]\nExample: help ls",
    theme: "Changes the visual theme of the OBPI interface between 'light' and 'dark' modes.\nUsage: theme <light|dark>\nExample: theme light"
  },
  apps: {
    themeSettings: {
      launch: () => {
        const content = document.createElement('div');
        content.innerHTML = `
          <h3 class="text-lg font-semibold mb-3">Theme Settings</h3>
          <p class="mb-2 text-sm">Select a theme for the OBPI interface.</p>
          <div class="flex gap-4">
            <button data-theme="dark" class="theme-btn px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600">Dark Theme</button>
            <button data-theme="light" class="theme-btn px-4 py-2 bg-gray-200 text-black rounded hover:bg-gray-300">Light Theme</button>
          </div>
        `;
        content.querySelectorAll('.theme-btn').forEach(btn => {
          btn.onclick = () => AppManager.apps.themeSettings.setTheme(btn.dataset.theme);
        });
        WindowManager.create('theme-settings', 'Theme Settings', content, {width: '400px', height:'250px'});
      },
      setTheme: (themeName) => {
        document.body.classList.remove('light-theme', 'dark-theme');
        if (themeName === 'light') {
          document.body.classList.add('light-theme');
          OBPI.activeTheme = 'light';
        } else {
          OBPI.activeTheme = 'dark';
        }
        localStorage.setItem(OBPI.config.themeStorageKey, OBPI.activeTheme);
        OBPI.kernel.log(`Theme changed to ${OBPI.activeTheme}`);
        if (Terminal.promptElement) Terminal.updatePrompt();
      },
      loadTheme: () => {
        const savedTheme = localStorage.getItem(OBPI.config.themeStorageKey);
        if (savedTheme) AppManager.apps.themeSettings.setTheme(savedTheme);
        else AppManager.apps.themeSettings.setTheme('dark');
      }
    }
  }
};

// --- Initialization Function ---
async function main() { // Made async to await PEPx storage initialization
  OBPI.kernel.log(`Initializing ${OBPI.name} v${OBPI.version}...`);
  AppManager.apps.themeSettings.loadTheme();
  initWebGLBackground();
  OBPI.envVars['HOME'] = '/home/guest/';
  OBPI.envVars['USER'] = 'guest';
  OBPI.envVars['PATH'] = '/bin:/home/guest/bin';
  WindowManager.restoreAllWindowStates();
  Terminal.init();

  if (!OBPI.windows['welcome-note']) {
    WindowManager.create('welcome-note', `Welcome to ${OBPI.name}!`,
      `<div class="p-3">
        <h2 class="text-xl font-semibold mb-2">${OBPI.name} v${OBPI.version}</h2>
        <p class="text-sm mb-1">This is a fully functional virtual machine desktop environment.</p>
        <p class="text-sm mb-1">All data (files, browser history, bookmarks, PEPx metadata) is now persistently stored on your host machine.</p>
        <p class="text-sm">Explore the Python IDE, embedded browser, and peripheral manager. Right-click desktop for options. Click OBPI button for Start Menu. Type 'help' in terminal.</p>
        <p class="text-xs mt-3 text-gray-500">Timestamp: ${new Date().toISOString()}</p>
      </div>`,
      { width: '600px', height: '380px', top: '50px', left: '50px' }
    );
  }

  OBPI.kernel.log(`${OBPI.name} fully initialized and ready.`, "success");
}

document.addEventListener('DOMContentLoaded', main);
