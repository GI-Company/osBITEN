class OBPITerminal {
    constructor() {
        this.history = [];
        this.historyIndex = 0;
        this.currentInput = '';
        this.promptSymbol = '➜';
        this.customCommands = new Map();
    }

    initialize() {
        this.terminal = document.querySelector('#obpi-terminal');
        this.content = this.terminal.querySelector('.terminal-content');
        
        this.setupInput();
        this.registerCommands();
        this.showWelcome();
    }

    setupInput() {
        this.input = document.createElement('input');
        this.input.className = 'terminal-input';
        this.input.setAttribute('spellcheck', 'false');
        
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.executeCommand(this.input.value);
            } else if (e.key === 'ArrowUp') {
                this.navigateHistory(-1);
            } else if (e.key === 'ArrowDown') {
                this.navigateHistory(1);
            }
        });
        
        this.content.appendChild(this.input);
        this.input.focus();
    }

    registerCommands() {
        // Register built-in commands
        this.customCommands.set('clear', () => this.clear());
        this.customCommands.set('help', () => this.showHelp());
        this.customCommands.set('system', async (args) => {
            if (args[0] === 'info') {
                return this.getSystemInfo();
            } else if (args[0] === 'processes') {
                return this.listProcesses();
            }
        });
    }

    async executeCommand(commandLine) {
        const [command, ...args] = commandLine.trim().split(' ');
        
        // Add to history
        this.history.push(commandLine);
        this.historyIndex = this.history.length;
        
        // Clear input
        this.input.value = '';
        
        // Print command
        this.print(`${this.promptSymbol} ${commandLine}`);
        
        try {
            if (this.customCommands.has(command)) {
                const result = await this.customCommands.get(command)(args);
                if (result) this.print(result);
            } else if (command) {
                // Try system command
                const result = await this.executeSystemCommand(command, args);
                this.print(result);
            }
        } catch (error) {
            this.printError(`Error: ${error.message}`);
        }
        
        // Scroll to bottom
        this.content.scrollTop = this.content.scrollHeight;
    }

    print(text, type = 'output') {
        const line = document.createElement('div');
        line.className = `terminal-line ${type}`;
        line.textContent = text;
        this.content.insertBefore(line, this.input);
    }

    printError(text) {
        this.print(text, 'error');
    }

    clear() {
        while (this.content.firstChild !== this.input) {
            this.content.removeChild(this.content.firstChild);
        }
    }

    showWelcome() {
        this.print('OBPI Terminal v2.0.0');
        this.print('Type "help" for available commands');
        this.print('');
    }
}