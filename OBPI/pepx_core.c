#include <emscripten.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// PEPx storage plane structure
typedef struct {
    uint8_t* data;
    uint32_t width;
    uint32_t height;
    uint32_t channels; // RGBA = 4
} PEPxPlane;

// PEPx storage context
typedef struct {
    PEPxPlane* planes;
    uint32_t plane_count;
    uint32_t dimensions;
    uint32_t bits_per_channel;
} PEPxContext;

// Global context
static PEPxContext* g_ctx = NULL;

// Initialize PEPx storage context
EMSCRIPTEN_KEEPALIVE
int32_t pepx_init(uint32_t dimensions, uint32_t plane_count) {
    if (g_ctx != NULL) {
        return -1; // Already initialized
    }

    g_ctx = (PEPxContext*)malloc(sizeof(PEPxContext));
    if (!g_ctx) return -2;

    g_ctx->dimensions = dimensions;
    g_ctx->plane_count = plane_count;
    g_ctx->bits_per_channel = 2; // Fixed 2 bits per channel as per spec
    g_ctx->planes = (PEPxPlane*)calloc(plane_count, sizeof(PEPxPlane));
    
    if (!g_ctx->planes) {
        free(g_ctx);
        g_ctx = NULL;
        return -3;
    }

    // Initialize each plane
    for (uint32_t i = 0; i < plane_count; i++) {
        g_ctx->planes[i].width = dimensions;
        g_ctx->planes[i].height = dimensions;
        g_ctx->planes[i].channels = 4; // RGBA
        size_t plane_size = dimensions * dimensions * 4;
        g_ctx->planes[i].data = (uint8_t*)malloc(plane_size);
        
        if (!g_ctx->planes[i].data) {
            // Cleanup on failure
            for (uint32_t j = 0; j < i; j++) {
                free(g_ctx->planes[j].data);
            }
            free(g_ctx->planes);
            free(g_ctx);
            g_ctx = NULL;
            return -4;
        }

        // Initialize with slight noise for steganography
        for (size_t j = 0; j < plane_size; j++) {
            g_ctx->planes[i].data[j] = (uint8_t)(rand() % 4);
        }
    }

    return 0; // Success
}

// Store data in pixels using LSB steganography
EMSCRIPTEN_KEEPALIVE
int32_t pepx_store_data(uint32_t plane_idx, uint32_t start_x, uint32_t start_y, 
                        const uint8_t* data, uint32_t length) {
    if (!g_ctx || plane_idx >= g_ctx->plane_count) return -1;
    
    PEPxPlane* plane = &g_ctx->planes[plane_idx];
    uint32_t max_pixels = plane->width * plane->height;
    uint32_t start_pixel = start_y * plane->width + start_x;
    
    if (start_pixel + length > max_pixels) return -2;

    // Each pixel stores 1 byte using 2 bits per channel (RGBA)
    for (uint32_t i = 0; i < length; i++) {
        uint32_t pixel_idx = start_pixel + i;
        uint32_t pixel_offset = pixel_idx * 4;
        uint8_t byte = data[i];

        // Split byte into 2-bit chunks for each channel
        plane->data[pixel_offset]     = (plane->data[pixel_offset]     & 0xFC) | ((byte >> 6) & 0x03);
        plane->data[pixel_offset + 1] = (plane->data[pixel_offset + 1] & 0xFC) | ((byte >> 4) & 0x03);
        plane->data[pixel_offset + 2] = (plane->data[pixel_offset + 2] & 0xFC) | ((byte >> 2) & 0x03);
        plane->data[pixel_offset + 3] = (plane->data[pixel_offset + 3] & 0xFC) | (byte & 0x03);
    }

    return 0;
}

// Retrieve data from pixels
EMSCRIPTEN_KEEPALIVE
int32_t pepx_retrieve_data(uint32_t plane_idx, uint32_t start_x, uint32_t start_y,
                          uint8_t* output, uint32_t length) {
    if (!g_ctx || plane_idx >= g_ctx->plane_count) return -1;
    
    PEPxPlane* plane = &g_ctx->planes[plane_idx];
    uint32_t max_pixels = plane->width * plane->height;
    uint32_t start_pixel = start_y * plane->width + start_x;
    
    if (start_pixel + length > max_pixels) return -2;

    // Extract bytes from pixels
    for (uint32_t i = 0; i < length; i++) {
        uint32_t pixel_idx = start_pixel + i;
        uint32_t pixel_offset = pixel_idx * 4;
        uint8_t byte = 0;

        // Combine 2-bit chunks from each channel
        byte |= (plane->data[pixel_offset]     & 0x03) << 6;
        byte |= (plane->data[pixel_offset + 1] & 0x03) << 4;
        byte |= (plane->data[pixel_offset + 2] & 0x03) << 2;
        byte |= (plane->data[pixel_offset + 3] & 0x03);

        output[i] = byte;
    }

    return 0;
}

// Get raw plane data for rendering
EMSCRIPTEN_KEEPALIVE
uint8_t* pepx_get_plane_data(uint32_t plane_idx) {
    if (!g_ctx || plane_idx >= g_ctx->plane_count) return NULL;
    return g_ctx->planes[plane_idx].data;
}

// Clean up resources
EMSCRIPTEN_KEEPALIVE
void pepx_cleanup(void) {
    if (!g_ctx) return;

    for (uint32_t i = 0; i < g_ctx->plane_count; i++) {
        free(g_ctx->planes[i].data);
    }
    free(g_ctx->planes);
    free(g_ctx);
    g_ctx = NULL;
}