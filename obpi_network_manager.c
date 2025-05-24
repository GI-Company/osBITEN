#include <netlink/netlink.h>
#include <netlink/route/link.h>
#include <wpa_ctrl.h>

typedef struct {
    struct nl_sock* nl_sock;
    struct wpa_ctrl* wpa_ctrl;
    char* wifi_interface;
} NetworkManager;

// WiFi Management
EMSCRIPTEN_KEEPALIVE
int32_t wifi_connect_network(const char* ssid, const char* psk) {
    NetworkManager* nm = get_network_manager();
    if (!nm) return -1;

    // Configure WPA Supplicant
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "ADD_NETWORK");
    if (wpa_ctrl_request(nm->wpa_ctrl, cmd, strlen(cmd), NULL, NULL, NULL) < 0) {
        return -2;
    }

    // Set network parameters
    snprintf(cmd, sizeof(cmd), "SET_NETWORK 0 ssid \"%s\"", ssid);
    wpa_ctrl_request(nm->wpa_ctrl, cmd, strlen(cmd), NULL, NULL, NULL);

    snprintf(cmd, sizeof(cmd), "SET_NETWORK 0 psk \"%s\"", psk);
    wpa_ctrl_request(nm->wpa_ctrl, cmd, strlen(cmd), NULL, NULL, NULL);

    // Enable and select network
    wpa_ctrl_request(nm->wpa_ctrl, "ENABLE_NETWORK 0", 14, NULL, NULL, NULL);
    
    return 0;
}

// Ethernet Management
EMSCRIPTEN_KEEPALIVE
int32_t ethernet_configure_interface(const char* interface) {
    NetworkManager* nm = get_network_manager();
    if (!nm) return -1;

    struct rtnl_link* link;
    struct nl_cache* link_cache;
    
    // Get interface information
    if (rtnl_link_alloc_cache(nm->nl_sock, AF_UNSPEC, &link_cache) < 0) {
        return -2;
    }

    // Configure interface
    link = rtnl_link_get_by_name(link_cache, interface);
    if (!link) {
        nl_cache_free(link_cache);
        return -3;
    }

    return 0;
}