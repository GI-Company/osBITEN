// Add to AppManager.installedApps
AppManager.installedApps['obpl_ide'] = {
    name: 'OBPL IDE',
    launch: () => AppManager.launch('obpl-ide', 'OBPL IDE', AppManager.apps.obplIDE.init(), {
        width: '800px',
        height: '600px'
    }),
    icon: '⌨️'
};

// Add to AppManager.apps
AppManager.apps.obplIDE = {
    obpl: null,
    editor: null,
    outputArea: null,

    init: () => {
        const content = document.createElement('div');
        content.className = 'w-full h-full flex flex-col p-4 bg-gray-100';
        content.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <div class="flex space-x-2">
                    <button id="obpl-run" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
                        ▶ Run
                    </button>
                    <button id="obpl-save" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        💾 Save
                    </button>
                </div>
                <select id="obpl-examples" class="px-4 py-2 border rounded">
                    <option value="">Select Example...</option>
                    <option value="hello">Hello World</option>
                    <option value="calc">Calculator</option>
                    <option value="loop">Loop Example</option>
                </select>
            </div>
            <div class="flex-grow flex flex-col">
                <div class="flex-grow">
                    <textarea id="obpl-editor" class="w-full h-full p-4 font-mono text-sm border rounded resize-none"></textarea>
                </div>
                <div class="h-40 mt-4">
                    <div id="obpl-output" class="w-full h-full p-4 font-mono text-sm bg-gray-800 text-white rounded overflow-y-auto"></div>
                </div>
            </div>
        `;

        const setupIDE = async () => {
            AppManager.apps.obplIDE.editor = content.querySelector('#obpl-editor');
            AppManager.apps.obplIDE.outputArea = content.querySelector('#obpl-output');
            
            if (!AppManager.apps.obplIDE.obpl) {
                AppManager.apps.obplIDE.obpl = new OBPLanguage();
                await AppManager.apps.obplIDE.obpl.initialize();
            }

            content.querySelector('#obpl-run').onclick = () => {
                const code = AppManager.apps.obplIDE.editor.value;
                AppManager.apps.obplIDE.runCode(code);
            };

            content.querySelector('#obpl-save').onclick = () => {
                const code = AppManager.apps.obplIDE.editor.value;
                AppManager.apps.obplIDE.saveCode();
            };

            content.querySelector('#obpl-examples').onchange = (e) => {
                const example = e.target.value;
                if (example) AppManager.apps.obplIDE.loadExample(example);
            };
        };

        setupIDE();
        return content;
    },

    runCode: async (code) => {
        try {
            AppManager.apps.obplIDE.outputArea.textContent = 'Running...\n';
            const result = await AppManager.apps.obplIDE.obpl.execute(code);
            AppManager.apps.obplIDE.outputArea.textContent += `Result: ${result}\n`;
        } catch (error) {
            AppManager.apps.obplIDE.outputArea.textContent += `Error: ${error.message}\n`;
        }
    },

    saveCode: () => {
        const code = AppManager.apps.obplIDE.editor.value;
        const blob = new Blob([code], { type: 'text/plain' });
        const filename = prompt('Enter filename:', 'program.obpl');
        if (filename) {
            // Use PEPx storage
            OBPI.pepxInstance.storeFile(
                new File([blob], filename),
                '/home/guest/obpl/'
            ).then(() => {
                AppManager.apps.obplIDE.outputArea.textContent += `Saved as ${filename}\n`;
            }).catch(error => {
                AppManager.apps.obplIDE.outputArea.textContent += `Error saving: ${error.message}\n`;
            });
        }
    },

    loadExample: (example) => {
        const examples = {
            hello: `print "Hello, OBPI!"`,
            calc: `
                let x = 10
                let y = 5
                print x + y
                print x * y
                print x / y
            `,
            loop: `
                for i in range(5):
                    print i
            `
        };
        AppManager.apps.obplIDE.editor.value = examples[example] || '';
    }
};