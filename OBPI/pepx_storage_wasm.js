class PEPxStorageWASM {
    constructor(dimensions = 19000) {
        this.dimensions = Math.min(dimensions, 4096);
        this.totalPlanes = 9;
        this.colorChannels = 4;
        this.bitsPerChannelComponent = 2;
        this.canvasElements = [];
        this.metadataStore = new PEPxMetadataStore('pepx_metadata_v0.6');
        this.isInitialized = false;
        this.wasmModule = null;
    }

    async initializeWASM() {
        try {
            // Load the WebAssembly module
            await Module.onRuntimeInitialized;
            this.wasmModule = {
                init: Module.cwrap('pepx_init', 'number', ['number', 'number']),
                storeData: Module.cwrap('pepx_store_data', 'number', 
                    ['number', 'number', 'number', 'array', 'number']),
                retrieveData: Module.cwrap('pepx_retrieve_data', 'number',
                    ['number', 'number', 'number', 'array', 'number']),
                getPlaneData: Module.cwrap('pepx_get_plane_data', 'number', ['number']),
                cleanup: Module.cwrap('pepx_cleanup', null, [])
            };

            // Initialize the PEPx storage in WASM
            const result = this.wasmModule.init(this.dimensions, this.totalPlanes);
            if (result !== 0) {
                throw new Error(`Failed to initialize PEPx WASM backend: ${result}`);
            }

        } catch (error) {
            OBPI.kernel.log(`PEPx WASM initialization failed: ${error.message}`, 'error');
            throw error;
        }
    }

    async initializeCanvases() {
        if (this.isInitialized) return;
        
        await this.initializeWASM();
        OBPI.kernel.log(`PEPxStorage: Initializing ${this.totalPlanes} canvas planes...`, 'info');
        
        for (let i = 0; i < this.totalPlanes; i++) {
            const canvas = document.createElement('canvas');
            canvas.width = this.dimensions;
            canvas.height = this.dimensions;
            
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            const imageData = ctx.createImageData(this.dimensions, this.dimensions);
            
            // Get the plane data from WASM
            const planeDataPtr = this.wasmModule.getPlaneData(i);
            const planeData = new Uint8Array(Module.HEAPU8.buffer, planeDataPtr, this.dimensions * this.dimensions * 4);
            
            // Copy the plane data to the canvas
            imageData.data.set(planeData);
            ctx.putImageData(imageData, 0, 0);
            
            this.canvasElements.push({
                id: `pepx-plane-${i}`,
                canvas: canvas,
                ctx: ctx
            });
        }
        
        this.isInitialized = true;
        OBPI.kernel.log(`PEPx: ${this.totalPlanes} storage planes initialized using WASM backend.`, 'success');
    }

    async storeFile(file, path) {
        if (!this.isInitialized) await this.initializeCanvases();
        
        try {
            const arrayBuffer = await this.readFileAsArrayBuffer(file);
            const dataToStore = new Uint8Array(arrayBuffer);
            
            const allocation = this.findFreeSpace(dataToStore.byteLength);
            if (!allocation) throw new Error('PEPx: Insufficient storage space.');
            
            // Store data using WASM backend
            const result = this.wasmModule.storeData(
                allocation.plane,
                allocation.startX,
                allocation.startY,
                dataToStore,
                dataToStore.length
            );
            
            if (result !== 0) {
                throw new Error(`PEPx WASM storage failed: ${result}`);
            }
            
            // Update canvas with new data
            const planeObj = this.canvasElements[allocation.plane];
            const planeDataPtr = this.wasmModule.getPlaneData(allocation.plane);
            const planeData = new Uint8Array(Module.HEAPU8.buffer, planeDataPtr, this.dimensions * this.dimensions * 4);
            const imageData = planeObj.ctx.createImageData(this.dimensions, this.dimensions);
            imageData.data.set(planeData);
            planeObj.ctx.putImageData(imageData, 0, 0);
            
            // Update metadata
            const fileId = this.generateUniqueId();
            this.metadataStore.addFile({
                id: fileId,
                name: file.name,
                path: path,
                size: file.size,
                storedByteLength: dataToStore.byteLength,
                type: file.type,
                allocation: allocation,
                created: new Date().toISOString(),
                modified: new Date().toISOString()
            });
            
            return fileId;
            
        } catch (error) {
            OBPI.kernel.log(`PEPx: Failed to store file: ${error.message}`, 'error');
            throw error;
        }
    }

    async retrieveFile(fileId) {
        if (!this.isInitialized) throw new Error('PEPx: Storage not initialized');
        
        const metadata = this.metadataStore.getFile(fileId);
        if (!metadata) throw new Error(`PEPx: File metadata not found for ID: ${fileId}`);
        
        // Create output buffer
        const outputData = new Uint8Array(metadata.storedByteLength);
        
        // Retrieve data using WASM backend
        const result = this.wasmModule.retrieveData(
            metadata.allocation.plane,
            metadata.allocation.startX,
            metadata.allocation.startY,
            outputData,
            metadata.storedByteLength
        );
        
        if (result !== 0) {
            throw new Error(`PEPx WASM retrieval failed: ${result}`);
        }
        
        return new Blob([outputData.buffer], { type: metadata.type });
    }

    // ... rest of the PEPxStorage methods remain the same ...
}