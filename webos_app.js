class WebOSApp {
    constructor() {
        this.bridge = null;
        this.vmManager = null;
        this.displayServer = null;
    }

    async initialize() {
        // Initialize WebOS bridge
        this.bridge = new WebOSBridge();
        await this.bridge.initialize();

        // Initialize VM manager
        this.vmManager = new VMManager();
        await this.vmManager.initialize({
            maxInstances: 4,
            memoryPerInstance: 256 * 1024 * 1024, // 256MB
            cpuCores: 2
        });

        // Initialize display server
        this.displayServer = new DisplayServer();
        await this.displayServer.initialize({
            width: window.innerWidth,
            height: window.innerHeight,
            format: 'RGBA8888'
        });

        // Register with WebOS system
        await webOS.service.request('luna://com.webos.service.applicationmanager', {
            method: 'register',
            parameters: {
                id: 'com.obpi.system',
                version: '2.0.0',
                vendor: 'GI-Company'
            }
        });
    }

    async createVM(config) {
        const vm = await this.vmManager.createInstance(config);
        
        // Create WebOS card for VM
        const cardId = await webOS.service.request('luna://com.webos.service.cards', {
            method: 'create',
            parameters: {
                title: config.name,
                subtitle: 'Virtual Machine',
                windowType: 'card',
                displayId: vm.displayId
            }
        });

        return { vm, cardId };
    }

    handleWebOSEvents() {
        document.addEventListener('webOSLaunch', (e) => {
            this.onLaunch(e.detail);
        });

        document.addEventListener('webOSRelaunch', (e) => {
            this.onRelaunch(e.detail);
        });

        window.addEventListener('resize', () => {
            this.displayServer.resize(window.innerWidth, window.innerHeight);
        });
    }
}