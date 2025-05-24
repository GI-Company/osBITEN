#include <emscripten.h>
#include <webos_platform.h>

typedef struct {
    luna_service_t* luna;
    webos_display_t* display;
    webos_input_t* input;
    webos_network_t* network;
} WebOSContext;

EMSCRIPTEN_KEEPALIVE
int32_t webos_init_platform() {
    WebOSContext* ctx = malloc(sizeof(WebOSContext));
    if (!ctx) return -1;

    // Initialize Luna Service Bus
    ctx->luna = luna_service_initialize("com.obpi.core");
    if (!ctx->luna) goto cleanup;

    // Register system services
    luna_service_register(ctx->luna, "/system", handle_system_calls);
    luna_service_register(ctx->luna, "/display", handle_display_calls);
    
    return 0;

cleanup:
    free(ctx);
    return -1;
}