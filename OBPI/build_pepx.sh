#!/bin/bash
emcc pepx_core.c \
    -O3 \
    -s WASM=1 \
    -s EXPORTED_FUNCTIONS='["_pepx_init", "_pepx_store_data", "_pepx_retrieve_data", "_pepx_get_plane_data", "_pepx_cleanup"]' \
    -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]' \
    -s ALLOW_MEMORY_GROWTH=1 \
    -s INITIAL_MEMORY=16MB \
    -s MAXIMUM_MEMORY=512MB \
    -o pepx_core.js