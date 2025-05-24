/**
 * OBPI Process Manager v0.7
 * Advanced Process Control and Resource Orchestration
 */
class ProcessManager {
    constructor() {
        this.version = '0.7.0';
        this.processes = new Map();
        this.threads = new Map();
        this.ipcChannels = new Map();
        this.schedulingQueues = new Array(32).fill().map(() => []); // 32 priority levels
        this.realTimeProcesses = new Set();
        
        // Process Groups and Sessions
        this.processGroups = new Map();
        this.sessions = new Map();
        
        // Resource Limits
        this.resourceLimits = {
            maxProcesses: 1000,
            maxThreadsPerProcess: 64,
            maxFileDescriptors: 1024,
            maxMemoryPerProcess: 1024 * 1024 * 1024, // 1GB
            maxCPUTimePerProcess: 60000, // 60 seconds
        };

        // Process Accounting
        this.accounting = {
            startTime: Date.now(),
            totalProcesses: 0,
            activeProcesses: 0,
            zombieProcesses: 0,
            cpuUsage: new Map(),
            memoryUsage: new Map(),
            ioOperations: new Map()
        };

        // IPC Management
        this.ipcManager = {
            messageQueues: new Map(),
            sharedMemory: new Map(),
            semaphores: new Map(),
            pipes: new Map()
        };

        // Process Scheduling
        this.scheduler = {
            quantum: 20, // ms
            priorityBoost: 1,
            agingInterval: 1000,
            preemptEnabled: true
        };

        // Security Context
        this.securityContext = {
            uidMap: new Map(),
            gidMap: new Map(),
            capabilities: new Map(),
            namespaces: new Map()
        };

        // Process State Management
        this.stateManager = {
            suspended: new Set(),
            blocked: new Set(),
            zombies: new Set(),
            orphans: new Set()
        };

        // Performance Monitoring
        this.performanceMonitor = {
            metrics: new Map(),
            thresholds: new Map(),
            alerts: [],
            samplingInterval: 1000
        };
    }

    async initialize() {
        this.log('Initializing OBPI Process Manager v0.7', 'info');
        
        // Initialize process namespaces
        await this.initializeNamespaces();
        
        // Set up IPC mechanisms
        await this.initializeIPC();
        
        // Initialize scheduler
        await this.initializeScheduler();
        
        // Set up performance monitoring
        await this.initializePerformanceMonitoring();
        
        // Start system processes
        await this.startSystemProcesses();
        
        return true;
    }

    async createProcess(options = {}) {
        const {
            executable,
            priority = 15,
            parentPid = null,
            env = {},
            args = [],
            cwd = '/',
            uid = 1000,
            gid = 1000,
            capabilities = new Set()
        } = options;

        // Check resource limits
        if (this.processes.size >= this.resourceLimits.maxProcesses) {
            throw new Error('Maximum process limit reached');
        }

        // Generate new PID
        const pid = this.generatePID();

        // Create process object
        const process = {
            pid,
            parentPid,
            executable,
            priority,
            state: 'CREATED',
            startTime: Date.now(),
            env: { ...process.env, ...env },
            args,
            cwd,
            uid,
            gid,
            capabilities: new Set(capabilities),
            threads: new Map(),
            fds: new Map(),
            children: new Set(),
            exitCode: null,
            sessionId: this.generateSessionId(),
            groupId: this.generateGroupId(),
            resources: new ResourceTracker(),
            metrics: new ProcessMetrics(),
            namespace: await this.createNamespace(pid),
            securityContext: await this.createSecurityContext(uid, gid, capabilities)
        };

        // Initialize process resources
        await this.initializeProcessResources(process);

        // Set up process environment
        await this.setupProcessEnvironment(process);

        // Add to process table
        this.processes.set(pid, process);
        this.accounting.totalProcesses++;
        this.accounting.activeProcesses++;

        // Update parent process if exists
        if (parentPid && this.processes.has(parentPid)) {
            this.processes.get(parentPid).children.add(pid);
        }

        this.log(`Created process ${pid} (Parent: ${parentPid || 'none'})`, 'info');
        return pid;
    }

    async startProcess(pid) {
        const process = this.processes.get(pid);
        if (!process) {
            throw new Error(`Process ${pid} not found`);
        }

        try {
            // Prepare execution context
            const context = await this.prepareExecutionContext(process);

            // Create main thread
            const mainThreadId = await this.createThread(process, process.executable);
            process.mainThreadId = mainThreadId;

            // Update process state
            process.state = 'RUNNING';
            process.startTime = Date.now();

            // Add to appropriate scheduling queue
            this.schedulingQueues[process.priority].push(pid);

            // Start performance monitoring
            this.startProcessMonitoring(pid);

            this.log(`Started process ${pid}`, 'info');
            return true;
        } catch (error) {
            this.handleProcessError(pid, error);
            return false;
        }
    }

    async createThread(process, threadFunction) {
        if (process.threads.size >= this.resourceLimits.maxThreadsPerProcess) {
            throw new Error(`Maximum thread limit reached for process ${process.pid}`);
        }

        const threadId = this.generateThreadId();
        const thread = {
            id: threadId,
            pid: process.pid,
            state: 'CREATED',
            startTime: Date.now(),
            cpuTime: 0,
            priority: process.priority,
            context: await this.createThreadContext()
        };

        // Create Web Worker for thread
        const workerCode = `
            self.onmessage = function(e) {
                try {
                    const result = (${threadFunction.toString()})(...e.data.args);
                    self.postMessage({ type: 'success', result });
                } catch (error) {
                    self.postMessage({ type: 'error', error: error.message });
                }
            };
        `;

        const blob = new Blob([workerCode], { type: 'application/javascript' });
        thread.worker = new Worker(URL.createObjectURL(blob));

        // Set up thread message handling
        thread.worker.onmessage = (e) => this.handleThreadMessage(threadId, e);
        thread.worker.onerror = (e) => this.handleThreadError(threadId, e);

        process.threads.set(threadId, thread);
        this.threads.set(threadId, thread);

        return threadId;
    }

    async terminateProcess(pid, exitCode = 0) {
        const process = this.processes.get(pid);
        if (!process) return false;

        try {
            // Terminate all threads
            for (const [threadId, thread] of process.threads) {
                await this.terminateThread(threadId);
            }

            // Clean up resources
            await this.cleanupProcessResources(process);

            // Handle child processes
            for (const childPid of process.children) {
                if (this.processes.has(childPid)) {
                    const childProcess = this.processes.get(childPid);
                    childProcess.parentPid = 1; // Assign to init process
                    this.stateManager.orphans.add(childPid);
                }
            }

            // Update process state
            process.state = 'TERMINATED';
            process.exitCode = exitCode;
            process.endTime = Date.now();

            // Update accounting
            this.accounting.activeProcesses--;
            if (process.state === 'ZOMBIE') {
                this.accounting.zombieProcesses--;
            }

            // Remove from scheduling queues
            this.removeFromSchedulingQueues(pid);

            // Notify parent process
            if (process.parentPid && this.processes.has(process.parentPid)) {
                await this.sendSignal(process.parentPid, 'SIGCHLD', { childPid: pid, exitCode });
            }

            // Clean up IPC resources
            await this.cleanupIPCResources(pid);

            // Remove process entry
            this.processes.delete(pid);

            this.log(`Terminated process ${pid} with exit code ${exitCode}`, 'info');
            return true;
        } catch (error) {
            this.log(`Error terminating process ${pid}: ${error.message}`, 'error');
            return false;
        }
    }

    async cleanupProcessResources(process) {
        // Close file descriptors
        for (const [fd, resource] of process.fds) {
            try {
                await this.closeFileDescriptor(process.pid, fd);
            } catch (error) {
                this.log(`Error closing fd ${fd} for process ${process.pid}: ${error.message}`, 'warn');
            }
        }

        // Release memory
        await process.resources.releaseAll();

        // Clean up namespaces
        await this.cleanupNamespace(process.pid);

        // Remove from process groups
        this.removeFromProcessGroup(process.pid);

        // Clean up shared memory segments
        await this.cleanupSharedMemory(process.pid);

        // Remove semaphores
        await this.cleanupSemaphores(process.pid);
    }

    async sendSignal(pid, signal, data = {}) {
        const process = this.processes.get(pid);
        if (!process) {
            throw new Error(`Process ${pid} not found`);
        }

        try {
            switch (signal) {
                case 'SIGTERM':
                    await this.terminateProcess(pid);
                    break;
                case 'SIGKILL':
                    await this.terminateProcess(pid, 9);
                    break;
                case 'SIGSTOP':
                    await this.suspendProcess(pid);
                    break;
                case 'SIGCONT':
                    await this.resumeProcess(pid);
                    break;
                case 'SIGCHLD':
                    await this.handleChildSignal(pid, data);
                    break;
                default:
                    await this.handleCustomSignal(pid, signal, data);
            }

            return true;
        } catch (error) {
            this.log(`Error sending signal ${signal} to process ${pid}: ${error.message}`, 'error');
            return false;
        }
    }

    createIpcChannel(sourcePid, targetPid, options = {}) {
        const channelId = this.generateChannelId();
        const channel = {
            id: channelId,
            source: sourcePid,
            target: targetPid,
            created: Date.now(),
            options,
            messageQueue: [],
            status: 'active'
        };

        this.ipcChannels.set(channelId, channel);
        return channelId;
    }

    async sendMessage(channelId, message) {
        const channel = this.ipcChannels.get(channelId);
        if (!channel) {
            throw new Error(`IPC channel ${channelId} not found`);
        }

        if (channel.status !== 'active') {
            throw new Error(`IPC channel ${channelId} is not active`);
        }

        channel.messageQueue.push({
            timestamp: Date.now(),
            content: message,
            processed: false
        });

        // Notify target process
        await this.notifyIpcMessage(channel.target, channelId);
    }

    // Utility methods
    generatePID() {
        return `pid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateThreadId() {
        return `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateChannelId() {
        return `ipc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    log(message, level = 'info') {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            component: 'ProcessManager',
            version: this.version
        };
        
        console[level] || console.log(`[OBPI ProcessManager|${level.toUpperCase()}]: ${message}`);
    }
}

class ResourceTracker {
    constructor() {
        this.resources = new Map();
        this.usage = {
            memory: 0,
            cpu: 0,
            fds: 0
        };
    }

    async allocate(type, amount) {
        this.usage[type] += amount;
        return true;
    }

    async release(type, amount) {
        this.usage[type] = Math.max(0, this.usage[type] - amount);
        return true;
    }

    async releaseAll() {
        for (const type in this.usage) {
            this.usage[type] = 0;
        }
        this.resources.clear();
        return true;
    }
}

class ProcessMetrics {
    constructor() {
        this.startTime = Date.now();
        this.measurements = new Map();
        this.samples = [];
        this.alerts = [];
    }

    record(metric, value) {
        const timestamp = Date.now();
        if (!this.measurements.has(metric)) {
            this.measurements.set(metric, []);
        }
        this.measurements.get(metric).push({ timestamp, value });
    }
}

// Export the process manager
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ProcessManager,
        ResourceTracker,
        ProcessMetrics
    };
} else {
    window.ProcessManager = ProcessManager;
    window.ResourceTracker = ResourceTracker;
    window.ProcessMetrics = ProcessMetrics;
}