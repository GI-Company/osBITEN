#include "vm_core.h"

typedef struct {
    char* vm_name;
    uint32_t memory_size;
    uint32_t cpu_cores;
    VMState state;
    void* display_buffer;
} VMInstance;

typedef struct {
    VMInstance** instances;
    uint32_t instance_count;
    uint32_t max_instances;
    ResourceMonitor* monitor;
} VMManager;

// VM Instance Management
EMSCRIPTEN_KEEPALIVE
VMInstance* vm_create_instance(const char* name, VMConfig* config) {
    VMInstance* instance = malloc(sizeof(VMInstance));
    if (!instance) return NULL;
    
    instance->vm_name = strdup(name);
    instance->memory_size = config->memory_size;
    instance->cpu_cores = config->cpu_cores;
    instance->state = VM_STATE_STOPPED;
    
    // Allocate display buffer
    instance->display_buffer = malloc(config->display_width * 
                                    config->display_height * 4);
    
    return instance;
}

// Resource Management
EMSCRIPTEN_KEEPALIVE
int32_t vm_allocate_resources(VMInstance* instance) {
    // Allocate memory
    void* mem = memalign(PAGE_SIZE, instance->memory_size);
    if (!mem) return -1;
    
    // Set up virtual CPU cores
    for (uint32_t i = 0; i < instance->cpu_cores; i++) {
        if (vcpu_init(instance, i) != 0) {
            free(mem);
            return -2;
        }
    }
    
    return 0;
}