/**
 * OBPI Kernel v0.7
 * Advanced Process and Resource Management
 */
class OBPIKernel {
    constructor() {
        this.version = '0.7.0';
        this.processTable = new Map();
        this.resourceTable = new Map();
        this.schedulerInterval = 5; // Reduced from 10ms for better responsiveness
        this.quantum = 20; // CPU time slice in ms
        this.maxProcesses = 100;
        this.priorityLevels = 32;
        this.interruptHandlers = new Map();
        
        // New: Advanced memory management
        this.memoryManager = {
            totalMemory: 1024 * 1024 * 1024, // 1GB virtual memory
            pageSize: 4096, // 4KB pages
            pages: new Map(),
            freePages: [],
            swapFile: null
        };

        // New: I/O Scheduler
        this.ioScheduler = {
            queue: [],
            currentOperation: null,
            priorities: new Map(),
            bandwidth: 1024 * 1024 // 1MB/s simulated bandwidth
        };

        // New: Security Context
        this.securityContext = {
            currentDomain: 'user',
            capabilities: new Set(),
            securityPolicy: new Map(),
            isolationLevel: 'strict'
        };
    }

    async initialize() {
        this.log('Initializing OBPI Kernel v0.7', 'info');
        
        // Initialize memory management
        await this.initializeMemoryManagement();
        
        // Initialize process management
        await this.initializeProcessManagement();
        
        // Initialize I/O subsystem
        await this.initializeIO();
        
        // Initialize security
        await this.initializeSecurity();
        
        // Start core services
        await this.startCoreServices();
        
        // Initialize scheduler
        this.startScheduler();
    }

    async initializeMemoryManagement() {
        // Initialize virtual memory system
        this.memoryManager.pages = new Map();
        for (let i = 0; i < this.memoryManager.totalMemory / this.memoryManager.pageSize; i++) {
            this.memoryManager.freePages.push(i);
        }

        // Set up page table
        this.memoryManager.pageTable = new Map();
        
        // Initialize swap file
        this.memoryManager.swapFile = await this.createSwapFile(1024 * 1024 * 512); // 512MB swap
    }

    async createProcess(executable, priority = 15) {
        if (this.processTable.size >= this.maxProcesses) {
            throw new Error('Maximum process limit reached');
        }

        const pid = this.generatePID();
        const process = {
            pid,
            executable,
            priority,
            state: 'READY',
            resources: new Set(),
            memoryPages: new Set(),
            startTime: Date.now(),
            cpuTime: 0,
            lastScheduled: 0,
            securityContext: this.createSecurityContext(),
            capabilities: new Set(),
            threadPool: new ThreadPool(4)
        };

        // Allocate memory pages
        const allocatedPages = await this.allocateMemory(process, 1024 * 1024); // 1MB initial allocation
        if (!allocatedPages) {
            throw new Error('Failed to allocate memory for process');
        }

        this.processTable.set(pid, process);
        return pid;
    }

    async allocateMemory(process, size) {
        const pagesNeeded = Math.ceil(size / this.memoryManager.pageSize);
        const allocatedPages = [];

        for (let i = 0; i < pagesNeeded; i++) {
            if (this.memoryManager.freePages.length === 0) {
                // Need to swap
                await this.swapOutLeastUsedPages();
            }

            const pageNumber = this.memoryManager.freePages.pop();
            if (pageNumber === undefined) {
                // Rollback allocation
                allocatedPages.forEach(page => this.memoryManager.freePages.push(page));
                return null;
            }

            allocatedPages.push(pageNumber);
            process.memoryPages.add(pageNumber);
        }

        return allocatedPages;
    }

    async swapOutLeastUsedPages() {
        const lruPages = [...this.memoryManager.pageTable.entries()]
            .sort((a, b) => a[1].lastAccessed - b[1].lastAccessed)
            .slice(0, 10); // Swap out 10 pages at a time

        for (const [pageNumber, pageInfo] of lruPages) {
            await this.swapOutPage(pageNumber, pageInfo);
            this.memoryManager.freePages.push(pageNumber);
        }
    }

    createSecurityContext() {
        return {
            uid: this.generateUID(),
            gid: this.generateGID(),
            capabilities: new Set(['base']),
            isolationLevel: this.securityContext.isolationLevel,
            securityPolicy: new Map(this.securityContext.securityPolicy)
        };
    }

    startScheduler() {
        setInterval(() => {
            this.scheduleProcesses();
            this.manageResources();
            this.checkSecurityPolicy();
        }, this.schedulerInterval);
    }

    scheduleProcesses() {
        const now = Date.now();
        let highestPriorityProcess = null;
        let highestPriority = -1;

        for (const [pid, process] of this.processTable) {
            if (process.state === 'READY') {
                const effectivePriority = this.calculateEffectivePriority(process);
                if (effectivePriority > highestPriority) {
                    highestPriority = effectivePriority;
                    highestPriorityProcess = process;
                }
            }
        }

        if (highestPriorityProcess) {
            this.executeProcess(highestPriorityProcess);
        }
    }

    calculateEffectivePriority(process) {
        const base = process.priority;
        const waitingTime = Date.now() - process.lastScheduled;
        const waitBonus = Math.floor(waitingTime / 1000); // Bonus point per second waiting
        const ioBonus = this.calculateIOBonus(process);
        
        return Math.min(this.priorityLevels - 1, base + waitBonus + ioBonus);
    }

    async executeProcess(process) {
        if (!this.checkResources(process)) {
            process.state = 'WAITING';
            return;
        }

        try {
            process.state = 'RUNNING';
            process.lastScheduled = Date.now();

            // Execute in isolated context
            await this.executeInIsolation(process);

            process.cpuTime += this.quantum;
            process.state = 'READY';
        } catch (error) {
            this.handleProcessError(process, error);
        }
    }

    async executeInIsolation(process) {
        return new Promise((resolve, reject) => {
            const workerCode = `
                self.onmessage = function(e) {
                    try {
                        const result = (${process.executable.toString()})();
                        self.postMessage({ type: 'success', result });
                    } catch (error) {
                        self.postMessage({ type: 'error', error: error.message });
                    }
                };
            `;

            const blob = new Blob([workerCode], { type: 'application/javascript' });
            const worker = new Worker(URL.createObjectURL(blob));

            worker.onmessage = (e) => {
                URL.revokeObjectURL(worker.objectURL);
                worker.terminate();
                
                if (e.data.type === 'success') {
                    resolve(e.data.result);
                } else {
                    reject(new Error(e.data.error));
                }
            };

            worker.onerror = (error) => {
                URL.revokeObjectURL(worker.objectURL);
                worker.terminate();
                reject(error);
            };

            worker.postMessage('start');

            // Enforce quantum
            setTimeout(() => {
                worker.terminate();
                reject(new Error('Process exceeded time quantum'));
            }, this.quantum);
        });
    }

    handleProcessError(process, error) {
        this.log(`Process ${process.pid} failed: ${error.message}`, 'error');
        process.state = 'ERROR';
        
        // Attempt recovery
        if (this.canRecoverProcess(process)) {
            this.restartProcess(process);
        } else {
            this.terminateProcess(process.pid);
        }
    }

    terminateProcess(pid) {
        const process = this.processTable.get(pid);
        if (!process) return;

        // Clean up resources
        this.releaseProcessResources(process);
        
        // Free memory
        this.freeProcessMemory(process);
        
        // Remove from process table
        this.processTable.delete(pid);
    }

    releaseProcessResources(process) {
        process.resources.forEach(resource => {
            const resourceData = this.resourceTable.get(resource);
            if (resourceData) {
                resourceData.locked = false;
                this.resourceTable.set(resource, resourceData);
            }
        });
    }

    freeProcessMemory(process) {
        process.memoryPages.forEach(pageNumber => {
            this.memoryManager.freePages.push(pageNumber);
            this.memoryManager.pageTable.delete(pageNumber);
        });
    }

    log(message, level = 'info') {
        const timestamp = new Date().toISOString();
        const formattedMessage = `[OBPI Kernel|${level.toUpperCase()}|${timestamp}]: ${message}`;
        
        // Console logging
        console[level] || console.log(formattedMessage);
        
        // System log
        this.systemLog.push({
            timestamp,
            level,
            message,
            kernel_version: this.version
        });

        // Trim log if too large
        if (this.systemLog.length > 1000) {
            this.systemLog = this.systemLog.slice(-500);
        }
    }

    // Utility methods
    generatePID() {
        return `pid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateUID() {
        return Math.floor(1000 + Math.random() * 9000);
    }

    generateGID() {
        return Math.floor(100 + Math.random() * 900);
    }
}

// Export the kernel
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OBPIKernel;
} else {
    window.OBPIKernel = OBPIKernel;
}