class WebOSService {
    constructor() {
        this.luna = null;
        this.subscriptions = new Map();
    }

    async initialize() {
        this.luna = await webOS.service.request("luna://com.obpi.core");
        
        // Register system services
        await this.registerServices([
            'com.obpi.core.system',
            'com.obpi.core.display',
            'com.obpi.core.network'
        ]);
    }

    async registerServices(services) {
        for (const service of services) {
            await this.luna.register(service);
        }
    }

    // Handle WebOS-specific events
    handleWebOSEvent(event) {
        switch (event.type) {
            case 'webOSLaunch':
                this.onLaunch(event.detail);
                break;
            case 'webOSRelaunch':
                this.onRelaunch(event.detail);
                break;
            case 'webOSLocaleChange':
                this.onLocaleChange(event.detail);
                break;
        }
    }
}