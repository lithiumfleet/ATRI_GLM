#include "chatglm.h"
#include <iomanip>
#include <iostream>
#include <fstream>
#include <ctime>

#ifdef _WIN32
#include <codecvt>
#include <fcntl.h>
#include <io.h>
#include <windows.h>
#endif

enum InferenceMode {
    INFERENCE_MODE_CHAT,
    INFERENCE_MODE_GENERATE,
};

static inline InferenceMode to_inference_mode(const std::string &s) {
    static std::unordered_map<std::string, InferenceMode> m{{"chat", INFERENCE_MODE_CHAT},
                                                            {"generate", INFERENCE_MODE_GENERATE}};
    return m.at(s);
}

struct Args {
    std::string model_path = "chatglm-ggml.bin";
    InferenceMode mode = INFERENCE_MODE_CHAT;
    std::string prompt = "你好";
    int max_length = 2048;
    int max_context_length = 512;
    bool interactive = false;
    int top_k = 0;
    float top_p = 0.7;
    float temp = 0.95;
    float repeat_penalty = 1.0;
    int num_threads = 0;
    bool verbose = false;
    std::string sys_prompt_fpath = "";
    std::string history_saving_dir = "";
};

static void usage(const std::string &prog) {
    std::cout << "Usage: " << prog << " [options]\n"
              << "\n"
              << "options:\n"
              << "  -h, --help              show this help message and exit\n"
              << "  -m, --model PATH        model path (default: chatglm-ggml.bin)\n"
              << "  --mode                  inference mode chose from {chat, generate} (default: chat)\n"
              << "  -p, --prompt PROMPT     prompt to start generation with (default: 你好)\n"
              << "  -i, --interactive       run in interactive mode\n"
              << "  -l, --max_length N      max total length including prompt and output (default: 2048)\n"
              << "  -c, --max_context_length N\n"
              << "                          max context length (default: 512)\n"
              << "  --top_k N               top-k sampling (default: 0)\n"
              << "  --top_p N               top-p sampling (default: 0.7)\n"
              << "  --temp N                temperature (default: 0.95)\n"
              << "  --repeat_penalty N      penalize repeat sequence of tokens (default: 1.0, 1.0 = disabled)\n"
              << "  -t, --threads N         number of threads for inference\n"
              << "  -v, --verbose           display verbose output including config/system/performance info\n"
              << "  -s, --sys_prompt_fpath  set system prompt from a file\n"
              << "  -d, --history_save_dir  dialog will be saved in directory\n";
}

static Args parse_args(const std::vector<std::string> &argv) {
    Args args;

    for (size_t i = 1; i < argv.size(); i++) {
        const std::string &arg = argv[i];

        if (arg == "-h" || arg == "--help") {
            usage(argv[0]);
            exit(EXIT_SUCCESS);
        } else if (arg == "-m" || arg == "--model") {
            args.model_path = argv[++i];
        } else if (arg == "--mode") {
            args.mode = to_inference_mode(argv[++i]);
        } else if (arg == "-p" || arg == "--prompt") {
            args.prompt = argv[++i];
        } else if (arg == "-i" || arg == "--interactive") {
            args.interactive = true;
        } else if (arg == "-l" || arg == "--max_length") {
            args.max_length = std::stoi(argv[++i]);
        } else if (arg == "-c" || arg == "--max_context_length") {
            args.max_context_length = std::stoi(argv[++i]);
        } else if (arg == "--top_k") {
            args.top_k = std::stoi(argv[++i]);
        } else if (arg == "--top_p") {
            args.top_p = std::stof(argv[++i]);
        } else if (arg == "--temp") {
            args.temp = std::stof(argv[++i]);
        } else if (arg == "--repeat_penalty") {
            args.repeat_penalty = std::stof(argv[++i]);
        } else if (arg == "-t" || arg == "--threads") {
            args.num_threads = std::stoi(argv[++i]);
        } else if (arg == "-v" || arg == "--verbose") {
            args.verbose = true;
        } else if (arg == "-s" || arg == "--sys_prompt_fpath") {
            args.sys_prompt_fpath = argv[++i];
        } else if (arg == "-d" || arg == "--history_saving_dir") {
            args.history_saving_dir = argv[++i];
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            usage(argv[0]);
            exit(EXIT_FAILURE);
        }
    }

    return args;
}

static Args parse_args(int argc, char **argv) {
    std::vector<std::string> argv_vec;
    argv_vec.reserve(argc);

#ifdef _WIN32
    LPWSTR *wargs = CommandLineToArgvW(GetCommandLineW(), &argc);
    CHATGLM_CHECK(wargs) << "failed to retrieve command line arguments";

    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    for (int i = 0; i < argc; i++) {
        argv_vec.emplace_back(converter.to_bytes(wargs[i]));
    }

    LocalFree(wargs);
#else
    for (int i = 0; i < argc; i++) {
        argv_vec.emplace_back(argv[i]);
    }
#endif

    return parse_args(argv_vec);
}

static bool get_utf8_line(std::string &line) {
#ifdef _WIN32
    std::wstring wline;
    bool ret = !!std::getline(std::wcin, wline);
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    line = converter.to_bytes(wline);
    return ret;
#else
    return !!std::getline(std::cin, line);
#endif
}

static std::vector<std::string> init_work_memery(std::string fpath) {
    std::vector<std::string> work_memery;
    try {
        std::ifstream fin(fpath, std::ios::in);
        std::string message;
        while(std::getline(fin, message)) {
            work_memery.emplace_back(message);
        }// no mannually close
    } catch (std::exception &e) {
        std::cerr << e.what() << std::endl;
        exit(EXIT_FAILURE);
    }
    return work_memery;
}

static std::vector<std::string> adjust_work_memery(const std::string& prompt, std::vector<std::string>& work_memery) {
    return work_memery; //FIXME!
}

void save_history(const std::vector<std::string>& history, std::string logdir) {
    if(logdir == "") {
        std::cerr << "History unsave. Please check your history_save_dir" << std::endl;
        return;
    }

    // get time
    std::time_t currentTime = std::time(nullptr);
    std::string dateTimeString = std::ctime(&currentTime);
    std::string fpath = logdir+'/';
    for(char c : dateTimeString) if(std::isdigit(c))fpath += c;
    fpath += ".txt";

    std::ofstream log_file(fpath);
    for(size_t i=0; i<history.size(); i++) {
        std::string line = history[i];
        // FIXME: remove all \n
        log_file << line << std::endl;
    }
    log_file.close();
}

static void chat(Args &args) {
    ggml_time_init();
    int64_t start_load_us = ggml_time_us();
    chatglm::Pipeline pipeline(args.model_path);
    int64_t end_load_us = ggml_time_us();

    std::string model_name = pipeline.model->config.model_type_name();
    if(model_name != "ChatGLM3") {
        std::cerr << "Sorry, This project for ChatGLM3 only. ¯\\_(ツ)_/¯" << std::flush;
        exit(EXIT_FAILURE);
    }
    auto text_streamer = std::make_shared<chatglm::TextStreamer>(std::cout, pipeline.tokenizer.get());
    auto perf_streamer = std::make_shared<chatglm::PerfStreamer>();
    auto streamer = std::make_shared<chatglm::StreamerGroup>(
        std::vector<std::shared_ptr<chatglm::BaseStreamer>>{text_streamer, perf_streamer});

    chatglm::GenerationConfig gen_config(args.max_length, args.max_context_length, args.temp > 0, args.top_k,
                                         args.top_p, args.temp, args.repeat_penalty, args.num_threads);

    if (args.verbose) {
        std::cout << "system info: | "
                  << "AVX = " << ggml_cpu_has_avx() << " | "
                  << "AVX2 = " << ggml_cpu_has_avx2() << " | "
                  << "AVX512 = " << ggml_cpu_has_avx512() << " | "
                  << "AVX512_VBMI = " << ggml_cpu_has_avx512_vbmi() << " | "
                  << "AVX512_VNNI = " << ggml_cpu_has_avx512_vnni() << " | "
                  << "FMA = " << ggml_cpu_has_fma() << " | "
                  << "NEON = " << ggml_cpu_has_neon() << " | "
                  << "ARM_FMA = " << ggml_cpu_has_arm_fma() << " | "
                  << "F16C = " << ggml_cpu_has_f16c() << " | "
                  << "FP16_VA = " << ggml_cpu_has_fp16_va() << " | "
                  << "WASM_SIMD = " << ggml_cpu_has_wasm_simd() << " | "
                  << "BLAS = " << ggml_cpu_has_blas() << " | "
                  << "SSE3 = " << ggml_cpu_has_sse3() << " | "
                  << "VSX = " << ggml_cpu_has_vsx() << " |\n";

        std::cout << "inference config: | "
                  << "max_length = " << args.max_length << " | "
                  << "max_context_length = " << args.max_context_length << " | "
                  << "top_k = " << args.top_k << " | "
                  << "top_p = " << args.top_p << " | "
                  << "temperature = " << args.temp << " | "
                  << "num_threads = " << args.num_threads << " |\n";

        std::cout << "loaded " << pipeline.model->config.model_type_name() << " model from " << args.model_path
                  << " within: " << (end_load_us - start_load_us) / 1000.f << " ms\n";

        std::cout << std::endl;
    }

    if (args.mode != INFERENCE_MODE_CHAT && args.interactive) {
        std::cerr << "interactive demo is only supported for chat mode, falling back to non-interactive one\n";
        args.interactive = false;
    }

    if (args.interactive) {
        std::cout << R"(=========================================)" << '\n'
                  << R"(                             _           )" << '\n'
                  << R"(   __,  -/- ,_   .     __   //  ,____,   )" << '\n'
                  << R"(  (_/(__/__/ (__/__ __(_/__(/__/ / / (_  )" << '\n'
                  << R"(                      _/_                )" << '\n'
                  << R"(                     (/                  )" << '\n'
                  << R"(=========================================)" << '\n'
                  << '\n'
                  << "Powered by ChatGLM.cpp! Press <Ctrl-c> to exit." << '\n'
                  << std::endl;

        std::vector<std::string> history;
        std::vector<std::string> work_memory;

        if (!args.sys_prompt_fpath.empty()) work_memory = init_work_memery(args.sys_prompt_fpath);
        
        while (1) {
            std::cout << std::setw(model_name.size()) << std::left
                      << " >>> " << std::flush;
            std::string prompt;

            // get prompt
            if (!get_utf8_line(prompt)) break;
            if (prompt.empty()) continue;
            if (prompt == "exit") break;

            adjust_work_memery(prompt, work_memory);

            work_memory.emplace_back(std::move("[usr]"+prompt));
            history.emplace_back(std::move("[usr]"+prompt));
            std::cout << "Atri" << " > ";
            std::string output = pipeline.chat(work_memory, gen_config, streamer.get());
            work_memory.emplace_back(std::move("[atri]"+output));
            history.emplace_back(std::move("[atri]"+output));

            if (args.verbose) {
                std::cout << "\n" << perf_streamer->to_string() << "\n\n";
            }
            perf_streamer->reset();
            
        }
        save_history(history,args.history_saving_dir);
        std::cout << "Bye\n";

    } else {
        if (args.mode == INFERENCE_MODE_CHAT) {
            pipeline.chat({args.prompt}, gen_config, streamer.get());
        } else {
            pipeline.generate(args.prompt, gen_config, streamer.get());
        }
        if (args.verbose) {
            std::cout << "\n" << perf_streamer->to_string() << "\n\n";
        }
    }
}

int main(int argc, char **argv) {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    _setmode(_fileno(stdin), _O_WTEXT);
#endif

    try {
        Args args = parse_args(argc, argv);
        chat(args);
    } catch (std::exception &e) {
        std::cerr << e.what() << std::endl;
        exit(EXIT_FAILURE);
    }
    return 0;
}
