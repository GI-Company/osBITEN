// In the OBPI initialization code
OBPI.pepxInstance = null;

// Modified initialization to handle WASM loading
async function initializePEPx() {
    try {
        const wasmPEPx = new PEPxStorageWASM();
        await wasmPEPx.initializeCanvases();
        OBPI.pepxInstance = wasmPEPx;
        OBPI.kernel.log('PEPx WASM backend initialized successfully', 'success');
    } catch (error) {
        OBPI.kernel.log(`PEPx WASM initialization failed, falling back to JS implementation: ${error.message}`, 'warn');
        // Fall back to original JS implementation
        OBPI.pepxInstance = new PEPxStorage();
        await OBPI.pepxInstance.initializeCanvases();
    }
}

// Update the relevant initialization calls to be async
// For example, in the PEPx Explorer app initialization:
apps.pepxExplorer.init = async () => {
    const content = document.createElement('div');
    content.style.width = '100%';
    content.style.height = '100%';
    content.style.overflow = 'hidden';

    if (!OBPI.pepxInstance) {
        await initializePEPx();
    }
    
    // ... rest of the initialization code ...
};