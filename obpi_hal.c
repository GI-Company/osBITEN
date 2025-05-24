#include "hal_core.h"

typedef struct {
    DisplayDriver* display;
    InputDriver* input;
    AudioDriver* audio;
    NetworkDriver* network;
    StorageDriver* storage;
} HALContext;

// Platform Detection and Initialization
EMSCRIPTEN_KEEPALIVE
int32_t hal_init_platform() {
    HALContext* ctx = malloc(sizeof(HALContext));
    if (!ctx) return -1;

    // Detect platform
    PlatformType platform = detect_platform();
    
    // Initialize appropriate drivers
    switch (platform) {
        case PLATFORM_WEBOS:
            ctx->display = &webos_display_driver;
            ctx->input = &webos_input_driver;
            ctx->audio = &webos_audio_driver;
            ctx->network = &webos_network_driver;
            ctx->storage = &webos_storage_driver;
            break;
            
        case PLATFORM_BROWSER:
            ctx->display = &html5_display_driver;
            ctx->input = &html5_input_driver;
            ctx->audio = &webaudio_driver;
            ctx->network = &websocket_driver;
            ctx->storage = &indexeddb_driver;
            break;
            
        case PLATFORM_NATIVE:
            ctx->display = &sdl_display_driver;
            ctx->input = &sdl_input_driver;
            ctx->audio = &alsa_driver;
            ctx->network = &socket_driver;
            ctx->storage = &filesystem_driver;
            break;
    }
    
    return 0;
}