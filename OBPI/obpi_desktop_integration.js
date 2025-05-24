// Add system tools to AppManager
AppManager.installedApps['system_monitor'] = {
    name: 'System Monitor',
    launch: () => AppManager.launch('system-monitor', 'OBPI System Monitor', 
        AppManager.apps.systemMonitor.init()),
    icon: '📊'
};

AppManager.installedApps['pentest_suite'] = {
    name: 'Pentest Suite',
    launch: () => AppManager.launch('pentest-suite', 'OBPI Pentest Suite', 
        AppManager.apps.pentestSuite.init()),
    icon: '🔒'
};

AppManager.installedApps['package_manager'] = {
    name: 'Package Manager',
    launch: () => AppManager.launch('package-manager', 'OBPI Package Manager', 
        AppManager.apps.packageManager.init()),
    icon: '📦'
};

// Add new CLI commands
AppManager.cliCommands.scan = async (args) => {
    if (!args[0]) {
        Terminal.print("scan: missing target", false, 'error');
        return;
    }
    const target = args[0];
    const scanType = args[1] || 'port';
    
    try {
        const result = await OBPI.system.scanTarget(target, scanType);
        Terminal.print(`Scan complete: ${result}`);
    } catch (error) {
        Terminal.print(`Scan error: ${error.message}`, false, 'error');
    }
};

AppManager.cliCommands.pkg = async (args) => {
    if (!args[0]) {
        Terminal.print("pkg: missing command", false, 'error');
        return;
    }
    
    const command = args[0];
    if (command === 'install') {
        if (!args[1]) {
            Terminal.print("pkg install: missing package name", false, 'error');
            return;
        }
        try {
            await OBPI.system.installPackage(args[1]);
            Terminal.print(`Package ${args[1]} installed successfully`);
        } catch (error) {
            Terminal.print(`Installation failed: ${error.message}`, false, 'error');
        }
    }
};