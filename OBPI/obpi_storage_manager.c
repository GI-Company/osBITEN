#include "storage_core.h"

typedef struct {
    char* mount_point;
    uint64_t total_size;
    uint64_t available;
    StorageType type;
} StorageDevice;

typedef struct {
    StorageDevice** devices;
    uint32_t device_count;
    PersistenceManager* persistence;
} StorageManager;

// Storage Device Management
EMSCRIPTEN_KEEPALIVE
StorageDevice* storage_mount_device(const char* device_path) {
    StorageDevice* dev = malloc(sizeof(StorageDevice));
    if (!dev) return NULL;

    // Mount external storage
    if (strncmp(device_path, "/dev/sd", 7) == 0) {
        // Handle USB storage
        mount_usb_storage(device_path, dev);
    } else if (strncmp(device_path, "/dev/mm", 7) == 0) {
        // Handle SD card
        mount_sd_storage(device_path, dev);
    }

    return dev;
}

// Persistence Management
EMSCRIPTEN_KEEPALIVE
int32_t persistence_init_manager() {
    PersistenceManager* pm = malloc(sizeof(PersistenceManager));
    if (!pm) return -1;

    // Initialize journal
    pm->journal = journal_create("/var/obpi/persistence.journal");
    if (!pm->journal) return -2;

    // Set up checkpoint system
    pm->checkpoint = checkpoint_init(60); // Checkpoint every 60 seconds
    
    return 0;
}