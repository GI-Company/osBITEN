#include <emscripten.h>
#include <SDL2/SDL.h>

// Widget types
typedef enum {
    WIDGET_WINDOW,
    WIDGET_BUTTON,
    WIDGET_INPUT,
    WIDGET_LABEL,
    WIDGET_LIST,
    WIDGET_CANVAS
} WidgetType;

// Widget structure
typedef struct Widget {
    WidgetType type;
    int x, y, width, height;
    char* text;
    void* data;
    struct Widget* parent;
    struct Widget** children;
    int child_count;
    void (*render)(struct Widget*);
    void (*handle_event)(struct Widget*, SDL_Event*);
} Widget;

// Theme structure
typedef struct {
    SDL_Color bg_color;
    SDL_Color fg_color;
    SDL_Color accent_color;
    char* font_family;
    int font_size;
} Theme;

EMSCRIPTEN_KEEPALIVE
Widget* gui_create_widget(WidgetType type, int x, int y, int width, int height) {
    Widget* widget = (Widget*)malloc(sizeof(Widget));
    if (!widget) return NULL;

    widget->type = type;
    widget->x = x;
    widget->y = y;
    widget->width = width;
    widget->height = height;
    widget->children = NULL;
    widget->child_count = 0;

    return widget;
}

EMSCRIPTEN_KEEPALIVE
int32_t gui_set_theme(Theme* theme) {
    // Apply theme to all widgets
    return 0;
}

EMSCRIPTEN_KEEPALIVE
int32_t gui_render(Widget* root) {
    // Render widget hierarchy
    return 0;
}