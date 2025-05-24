// Add to AppManager.cliCommands
AppManager.cliCommands.obpl = async (args) => {
    if (!args.length) {
        Terminal.print("OBPL (OBPI Programming Language) v1.0", false, 'info');
        Terminal.print("Usage:", false, 'info');
        Terminal.print("  obpl run <file.obpl>    - Run an OBPL program", false, 'info');
        Terminal.print("  obpl repl               - Start OBPL REPL", false, 'info');
        Terminal.print("  obpl help               - Show this help", false, 'info');
        return;
    }

    const command = args[0];
    
    if (command === 'run') {
        if (!args[1]) {
            Terminal.print("Error: Missing file path", false, 'error');
            return;
        }
        
        try {
            const file = await FileSystem.readFile(args[1]);
            if (!file) {
                Terminal.print(`Error: File not found: ${args[1]}`, false, 'error');
                return;
            }

            if (!AppManager.apps.obplIDE.obpl) {
                AppManager.apps.obplIDE.obpl = new OBPLanguage();
                await AppManager.apps.obplIDE.obpl.initialize();
            }

            const result = await AppManager.apps.obplIDE.obpl.execute(file.content);
            Terminal.print(`Program completed with result: ${result}`);
        } catch (error) {
            Terminal.print(`Error: ${error.message}`, false, 'error');
        }
    }
    else if (command === 'repl') {
        Terminal.print("OBPL REPL v1.0 (type 'exit' to quit)", false, 'info');
        Terminal.print(">>> ", false);
        
        if (!AppManager.apps.obplIDE.obpl) {
            AppManager.apps.obplIDE.obpl = new OBPLanguage();
            await AppManager.apps.obplIDE.obpl.initialize();
        }

        // Set up REPL mode
        Terminal.setREPLMode(true, async (input) => {
            if (input.trim().toLowerCase() === 'exit') {
                Terminal.setREPLMode(false);
                return;
            }

            try {
                const result = await AppManager.apps.obplIDE.obpl.execute(input);
                Terminal.print(`${result}`, false);
            } catch (error) {
                Terminal.print(`Error: ${error.message}`, false, 'error');
            }
            Terminal.print(">>> ", false);
        });
    }
    else if (command === 'help') {
        AppManager.cliCommands.obpl([]);
    }
    else {
        Terminal.print(`Unknown command: ${command}`, false, 'error');
        Terminal.print("Use 'obpl help' for usage information", false, 'info');
    }
};