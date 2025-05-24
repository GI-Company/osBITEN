#include <emscripten.h>
#include <tensorflow/lite/c/c_api.h>

// Command history entry
typedef struct {
    char* command;
    time_t timestamp;
    int success;
} CommandHistory;

// ML model context
typedef struct {
    TfLiteModel* model;
    TfLiteInterpreter* interpreter;
    CommandHistory* history;
    int history_size;
} MLBashContext;

EMSCRIPTEN_KEEPALIVE
int32_t ml_bash_init(const char* model_path) {
    MLBashContext* ctx = malloc(sizeof(MLBashContext));
    if (!ctx) return -1;

    // Load TFLite model
    ctx->model = TfLiteModelCreateFromFile(model_path);
    if (!ctx->model) return -2;

    // Initialize interpreter
    ctx->interpreter = TfLiteInterpreterCreate(ctx->model, NULL);
    if (!ctx->interpreter) return -3;

    return 0;
}

EMSCRIPTEN_KEEPALIVE
char* ml_bash_predict(const char* partial_command) {
    // Use TFLite model to predict next command
    return strdup("predicted_command");
}