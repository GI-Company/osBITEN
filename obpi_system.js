class OBPISystem {
    constructor() {
        this.initialized = false;
        this.core = null;
        this.pkg = null;
        this.gui = null;
        this.ide = null;
        this.mlBash = null;
    }

    async initialize() {
        if (this.initialized) return;

        // Initialize WASM modules
        await Module.onRuntimeInitialized;
        
        // Core system
        this.core = {
            init: Module.cwrap('obpi_core_init', 'number', ['string', 'string']),
            pentestScan: Module.cwrap('obpi_pentest_scan', 'number', ['string', 'string']),
            cleanup: Module.cwrap('obpi_core_cleanup', null, [])
        };

        // Package manager
        this.pkg = {
            init: Module.cwrap('pkg_init_cache', 'number', ['string']),
            update: Module.cwrap('pkg_update_index', 'number', ['string']),
            install: Module.cwrap('pkg_install', 'number', ['string'])
        };

        // GUI toolkit
        this.gui = {
            createWidget: Module.cwrap('gui_create_widget', 'number', 
                ['number', 'number', 'number', 'number', 'number']),
            setTheme: Module.cwrap('gui_set_theme', 'number', ['number']),
            render: Module.cwrap('gui_render', 'number', ['number'])
        };

        // IDE
        this.ide = {
            init: Module.cwrap('ide_init', 'number', ['string']),
            complete: Module.cwrap('ide_complete_at', 'number', 
                ['string', 'number', 'number']),
            analyze: Module.cwrap('ide_analyze_code', 'number', ['string'])
        };

        // ML-powered bash
        this.mlBash = {
            init: Module.cwrap('ml_bash_init', 'number', ['string']),
            predict: Module.cwrap('ml_bash_predict', 'string', ['string'])
        };

        // Initialize core system
        const result = this.core.init('GI-Company', JSON.stringify({
            gui_enabled: true,
            ml_enabled: true,
            pkg_enabled: true
        }));

        if (result !== 0) throw new Error('Failed to initialize OBPI System');
        
        this.initialized = true;
    }

    async installPackage(packageName) {
        if (!this.initialized) await this.initialize();
        return this.pkg.install(packageName);
    }

    async createWindow(title, width, height) {
        if (!this.initialized) await this.initialize();
        return this.gui.createWidget(0, 0, 0, width, height); // 0 = WIDGET_WINDOW
    }

    async predictCommand(partial) {
        if (!this.initialized) await this.initialize();
        return this.mlBash.predict(partial);
    }

    async scanTarget(target, scanType) {
        if (!this.initialized) await this.initialize();
        return this.core.pentestScan(target, scanType);
    }
}