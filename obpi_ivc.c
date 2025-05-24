#include "ivc_core.h"

typedef struct {
    char* channel_name;
    uint32_t buffer_size;
    void* shared_buffer;
    IVCCallback callback;
} IVCChannel;

// Channel Management
EMSCRIPTEN_KEEPALIVE
IVCChannel* ivc_create_channel(const char* name, uint32_t size) {
    IVCChannel* channel = malloc(sizeof(IVCChannel));
    if (!channel) return NULL;
    
    channel->channel_name = strdup(name);
    channel->buffer_size = size;
    channel->shared_buffer = malloc(size);
    
    return channel;
}

// Message Passing
EMSCRIPTEN_KEEPALIVE
int32_t ivc_send_message(IVCChannel* channel, const void* data, uint32_t size) {
    if (size > channel->buffer_size) return -1;
    
    memcpy(channel->shared_buffer, data, size);
    channel->callback(channel, IVC_EVENT_MESSAGE);
    
    return 0;
}