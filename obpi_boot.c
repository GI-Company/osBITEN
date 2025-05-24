#include <efi.h>
#include <efilib.h>

EFI_STATUS
EFIAPI
efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    InitializeLib(ImageHandle, SystemTable);
    Print(L"OBPI System Bootloader v1.0\n");

    // Load OBPI kernel
    // Initialize hardware abstraction
    // Start OBPI system

    return EFI_SUCCESS;
}