class OBPIKernel {
    constructor() {
        this.processes = new Map();
        this.resources = new Map();
        this.schedulerInterval = 10; // 10ms scheduler tick
        this.loadingPhases = [
            'BIOS', 'Bootloader', 'Kernel', 'System', 'Desktop'
        ];
    }

    async initialize() {
        this.updateBootProgress('Initializing Kernel', 0);
        
        // Initialize system components
        await this.initMemoryManager();
        await this.initProcessManager();
        await this.initDeviceManager();
        await this.initFileSystem();
        
        // Start system services
        this.startSystemServices();
        
        // Initialize scheduler
        this.startScheduler();
    }

    async bootSequence() {
        for (let i = 0; i < this.loadingPhases.length; i++) {
            const phase = this.loadingPhases[i];
            const progress = (i + 1) / this.loadingPhases.length * 100;
            
            await this.loadPhase(phase, progress);
        }
        
        await this.startDesktopEnvironment();
    }

    async loadPhase(phase, progress) {
        this.updateBootProgress(`Loading ${phase}...`, progress);
        
        // Simulate phase loading with resource checks
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Verify phase completion
        if (!this.verifyPhase(phase)) {
            throw new Error(`Failed to load ${phase}`);
        }
    }

    updateBootProgress(status, progress) {
        const bootStatus = document.querySelector('.boot-status');
        const progressBar = document.querySelector('.progress-fill');
        
        bootStatus.textContent = status;
        progressBar.style.transform = `scaleX(${progress / 100})`;
    }

    startScheduler() {
        setInterval(() => {
            this.processes.forEach(process => {
                if (process.state === 'READY') {
                    this.executeProcess(process);
                }
            });
        }, this.schedulerInterval);
    }

    async createProcess(executable, priority = 1) {
        const pid = this.generatePID();
        const process = {
            pid,
            executable,
            priority,
            state: 'READY',
            resources: new Set(),
            startTime: Date.now()
        };
        
        this.processes.set(pid, process);
        return pid;
    }

    executeProcess(process) {
        // Check resource availability
        if (!this.checkResources(process)) {
            process.state = 'WAITING';
            return;
        }

        try {
            process.state = 'RUNNING';
            process.executable();
            process.state = 'READY';
        } catch (error) {
            console.error(`Process ${process.pid} failed:`, error);
            process.state = 'ERROR';
        }
    }

    checkResources(process) {
        let available = true;
        process.resources.forEach(resource => {
            if (this.resources.get(resource)?.locked) {
                available = false;
            }
        });
        return available;
    }
}