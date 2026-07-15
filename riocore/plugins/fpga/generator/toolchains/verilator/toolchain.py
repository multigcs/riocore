import importlib
import os
import re
import shutil
import sys

import magic


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = self.config["output_path"]
        self.riocore_path = config["riocore_path"]
        self.toolchain_path = self.config.get("toolchains_json", {}).get("verilator", "")
        if self.toolchain_path and not self.toolchain_path.endswith("bin"):
            self.toolchain_path = os.path.join(self.toolchain_path, "bin")

    @classmethod
    def info(cls):
        return {
            "url": "https://www.veripool.org/verilator/",
            "info": "verilog simulation",
            "description": "you need following packages to run: libsdl2-dev, libsdl2-image-dev, libsdl2-ttf-dev, fonts-dejavu-core\nand maybe verilator if oss-cad-suite is not installed",
        }

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.qdf")
        pins_generator.Pins(self.config).generate(path)
        if sys.platform == "linux":
            verilator = shutil.which("verilator")
            if verilator is None:
                print("WARNING: can not found toolchain installation in PATH: verilator")

        verilogs = " ".join(self.config["verilog_files"])

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Verilator")
        makefile_data.append("")
        if self.toolchain_path:
            makefile_data.append(f"PATH     := {self.toolchain_path}:$(PATH)")
            makefile_data.append("")
        makefile_data.append("PROJECT   := rio")
        makefile_data.append("TOP       := rio")
        makefile_data.append(f"VERILOGS  := {verilogs}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append("")
        makefile_data.append("VFLAGS = -O3 --x-assign fast --x-initial fast --noassert")
        makefile_data.append("SDL_CFLAGS = `sdl2-config --cflags`")
        makefile_data.append("SDL_LDFLAGS = `sdl2-config --libs` -lSDL2_image -lSDL2_ttf")
        makefile_data.append("")
        makefile_data.append("all: clean build load")
        makefile_data.append("")
        makefile_data.append("build: obj_dir/V$(TOP)")
        makefile_data.append("")
        makefile_data.append("obj_dir/V$(TOP): $(VERILOGS)")
        makefile_data.append('	verilator --cc --exe --build -j 0 -Wall  -Wno-lint -CFLAGS "${SDL_CFLAGS}" -LDFLAGS "${SDL_LDFLAGS}" main.cpp $(TOP).v')
        makefile_data.append("")
        makefile_data.append("load:")
        makefile_data.append("	obj_dir/Vrio")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf obj_dir")
        makefile_data.append("")
        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))

        pindict = {}
        for slot in self.config.get("slots", []):
            for pin_name, pin_data in slot["pins"].items():
                pos = pin_data.get("pos")
                varname = pin_data.get("varname")
                if pos and varname:
                    pindict[varname] = pos
        buffersize = max(self.config["buffer_size_in"], self.config["buffer_size_out"])
        boardimage = self.config.get("boardimage")
        t = magic.from_file(boardimage)
        boardimage_w, boardimage_h = re.search(r"(\d+) x (\d+)", t).groups()
        boardscale = 2

        main_cpp = []
        main_cpp.append("""
#include "Vrio.h"
#include "verilated.h"

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include <SDL.h>
#include <SDL_ttf.h>
#include <SDL_image.h>
""")

        spi_mosi = ""
        spi_miso = ""
        spi_sclk = ""
        spi_sel = ""
        for varname in pindict:
            if varname.endswith("_MOSI") and varname.startswith("PININ_"):
                spi_mosi = f"rio->{varname}"
            elif varname.endswith("_MISO") and varname.startswith("PINOUT_"):
                spi_miso = f"rio->{varname}"
            elif varname.endswith("_SCLK") and varname.startswith("PININ_"):
                spi_sclk = f"rio->{varname}"
            elif varname.endswith("_SEL") and varname.startswith("PININ_"):
                spi_sel = f"rio->{varname}"
        if spi_mosi and spi_miso and spi_sclk and spi_sel:
            main_cpp.append(f"#define SPI_MOSI {spi_mosi}")
            main_cpp.append(f"#define SPI_MISO {spi_miso}")
            main_cpp.append(f"#define SPI_SCLK {spi_sclk}")
            main_cpp.append(f"#define SPI_SEL {spi_sel}")
        else:
            print("  WARNING: no SPI insterface found, no interaction possible in verilator mode")

        graph_nw = max(int(boardimage_w) * boardscale, 800)
        graph_nh = 15
        graph_tw = 100
        main_cpp.append(f'#define WINDOW_TITLE "{self.config["name"]}"')
        main_cpp.append(f'#define BOARD_IMAGE "{boardimage}"')
        main_cpp.append(f"#define BOARD_IMAGE_W {boardimage_w}")
        main_cpp.append(f"#define BOARD_IMAGE_H {boardimage_h}")
        main_cpp.append(f"#define BUFFER_BYTES {buffersize // 8}")
        main_cpp.append(f"#define GRAPH_TX {0}")
        main_cpp.append(f"#define GRAPH_X {graph_tw}")
        main_cpp.append(f"#define GRAPH_Y {int(boardimage_h) * boardscale}")
        main_cpp.append(f"#define GRAPH_W {graph_nw - graph_tw}")
        main_cpp.append(f"#define GRAPH_H {len(pindict) * graph_nh}")
        main_cpp.append(f"#define GRAPH_TH {graph_nh}")
        main_cpp.append("")
        main_cpp.append(f"int image_w = {int(boardimage_w) * boardscale};")
        main_cpp.append(f"int image_h = {int(boardimage_h) * boardscale};")
        main_cpp.append(f"int window_w = {graph_nw};")
        main_cpp.append(f"int window_h = {int(boardimage_h) * boardscale} + GRAPH_H + 10;")
        main_cpp.append(f"int boardscale = {boardscale};")
        main_cpp.append("volatile uint8_t running = 1;")
        main_cpp.append("volatile uint8_t vcd_record = 0;")
        main_cpp.append("volatile uint8_t vcd_running = 0;")
        main_cpp.append("")

        for varname in pindict:
            main_cpp.append(f"bool hist_{varname.lower()}[GRAPH_W];")

        for varname in pindict:
            main_cpp.append(f"SDL_Texture *textTexture{varname} = NULL;")
            main_cpp.append(f"int textWidth{varname} = 0;")

        main_cpp.append("")
        main_cpp.append("void draw_pins(SDL_Renderer *sdl_renderer, Vrio *rio) {")
        main_cpp.append("    SDL_Rect rect;")
        for varname, pos in pindict.items():
            main_cpp.append(f"    if (rio->{varname} == 1) {{")
            main_cpp.append("        SDL_SetRenderDrawColor(sdl_renderer, 0, 255, 0, 255);")
            main_cpp.append("    } else {")
            main_cpp.append("        SDL_SetRenderDrawColor(sdl_renderer, 120, 0, 0, 255);")
            main_cpp.append("    }")
            main_cpp.append(f"    rect = {{{pos[0] * boardscale - 11}, {pos[1] * boardscale - 11}, {22}, {22}}};")
            main_cpp.append("    SDL_RenderFillRect(sdl_renderer, &rect);")
            main_cpp.append("")
            if varname.startswith("PININ_"):
                main_cpp.append("    SDL_SetRenderDrawColor(sdl_renderer, 255, 255, 255, 255);")
                main_cpp.append("    SDL_RenderDrawRect(sdl_renderer, &rect);")

        py = 10
        ph = graph_nh - 4
        for varname, pos in pindict.items():
            main_cpp.append("    SDL_SetRenderDrawColor(sdl_renderer, 50, 50, 50, 255);")
            main_cpp.append(f"    rect = {{GRAPH_X, GRAPH_Y + {py}, GRAPH_W, {ph}}};")
            main_cpp.append("    SDL_RenderFillRect(sdl_renderer, &rect);")

            main_cpp.append(f"    rect = {{GRAPH_TX + 2, GRAPH_Y + {py}, textWidth{varname}, {ph + 2}}};")
            main_cpp.append(f"    SDL_RenderCopy(sdl_renderer, textTexture{varname}, NULL, &rect);")

            main_cpp.append("    SDL_SetRenderDrawColor(sdl_renderer, 0, 255, 0, 255);")
            main_cpp.append("    for (int i = 0; i < GRAPH_W; i++) {")
            main_cpp.append(f"        if (hist_{varname.lower()}[i] == 1) {{")
            main_cpp.append(f"            rect = {{GRAPH_X + i, GRAPH_Y + {py}, {1}, {ph}}};")
            main_cpp.append("            SDL_RenderDrawRect(sdl_renderer, &rect);")
            main_cpp.append("        } else {")
            main_cpp.append(f"            SDL_RenderDrawLine(sdl_renderer, GRAPH_X + i, GRAPH_Y + {py} + {ph}, GRAPH_X + i + 1, GRAPH_Y + {py} + {ph});")
            main_cpp.append("        }")
            main_cpp.append("    }")
            py += graph_nh

        main_cpp.append("}")
        main_cpp.append("""
static void *run(void *arg) {
    Vrio* rio = (Vrio*)arg;

    printf("INFO: Press 'q' to quit.\\n");
    printf("INFO: Press 'r' to start/stop vcd recording.\\n");

    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("SDL ERROR: init failed.\\n");
        running = 0;
        return NULL;
    }

    if (TTF_Init() == -1) {
        printf("ERROR: SDL_ttf init failed.\\n");
        SDL_Quit();
        running = 0;
        return NULL;
    }

    TTF_Font* font = TTF_OpenFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", GRAPH_TH - 4);
    if (!font) {
        printf("ERROR: SDL_ttf/font init failed.\\n");
        TTF_Quit();
        SDL_Quit();
        running = 0;
        return NULL;
    }
    int imgFlags = IMG_INIT_PNG | IMG_INIT_JPG;
    if (!(IMG_Init(imgFlags) & imgFlags)) {
        printf("SDL_image init failed.\\n");
        SDL_Quit();
        return NULL;
    }

    SDL_Event    event;
    SDL_Rect     rect;
    SDL_Point    size;
    SDL_Color    White = {255, 255, 255};
    SDL_Window   *sdl_window   = NULL;
    SDL_Renderer *sdl_renderer = NULL;
    SDL_Texture  *sdl_texture  = NULL;
    SDL_Surface  *image_surface = IMG_Load(BOARD_IMAGE);

    sdl_window = SDL_CreateWindow(WINDOW_TITLE, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, window_w, window_h, SDL_WINDOW_SHOWN);
    if (!sdl_window) {
        printf("Window creation failed: %s\\n", SDL_GetError());
        running = 0;
        return NULL;
    }
    sdl_renderer = SDL_CreateRenderer(sdl_window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!sdl_renderer) {
        printf("Renderer creation failed: %s\\n", SDL_GetError());
        running = 0;
        return NULL;
    }
    sdl_texture = SDL_CreateTexture(sdl_renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET, window_w, window_h);
    if (!sdl_texture) {
        printf("Texture creation failed: %s\\n", SDL_GetError());
        running = 0;
        return NULL;
    }
    const Uint8 *keyb_state = SDL_GetKeyboardState(NULL);
    SDL_Texture *image_texture = SDL_CreateTextureFromSurface(sdl_renderer, image_surface);
    SDL_FreeSurface(image_surface);

    SDL_Color textColor = { 255, 255, 255, 255 };
    SDL_Surface *textSurface = NULL;
""")

        for varname in pindict:
            title = varname.split("_", 1)[1]
            main_cpp.append(f'    textSurface = TTF_RenderText_Blended(font, "{title}", textColor);')
            main_cpp.append(f"    textTexture{varname} = SDL_CreateTextureFromSurface(sdl_renderer, textSurface);")
            main_cpp.append(f"    textWidth{varname} = textSurface->w;")
            main_cpp.append("    SDL_FreeSurface(textSurface);")

        main_cpp.append("""

    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                printf("exit..\\n");
                running = 0;
                break;
            } else if (event.type == SDL_MOUSEBUTTONDOWN && event.button.button == SDL_BUTTON_LEFT) {""")

        for varname, pos in pindict.items():
            if varname.startswith("PININ_"):
                main_cpp.append(f"                if (abs(event.button.x / boardscale - {pos[0]}) < 6 && abs(event.button.y / boardscale - {pos[1]}) < 6) {{")
                main_cpp.append(f"                    rio->{varname} = 1 - rio->{varname};")
                main_cpp.append("                }")

        main_cpp.append("""            }
        }
        if (keyb_state[SDL_SCANCODE_Q]) {
            printf("exit..\\n");
            running = 0;
            break;
        } else if (keyb_state[SDL_SCANCODE_R]) {
            vcd_record = 1 - vcd_record;
            SDL_Delay(200);
        }
        SDL_SetRenderDrawColor(sdl_renderer, 0, 0, 0, 255);
        SDL_RenderClear(sdl_renderer);
        rect = {0, 0, image_w, image_h};
        SDL_RenderCopy(sdl_renderer, image_texture, NULL, &rect);
        draw_pins(sdl_renderer, rio);
        SDL_RenderPresent(sdl_renderer);
        SDL_Delay(40);
    }
    return NULL;
}

int main(int argc, char** argv) {
    uint8_t spi_tx[BUFFER_BYTES] = {0x74, 0x69, 0x72, 0x77};
    uint8_t spi_rx[BUFFER_BYTES];
    int spi_rx_num = 0;
    int spi_rx_bit = 0;
    int spi_rx_cs = 1;
    FILE *fd_gtkw = NULL;
    FILE *fd_vcd = NULL;

    VerilatedContext* contextp = new VerilatedContext;
    contextp->commandArgs(argc, argv);
    Vrio* rio = new Vrio{contextp};
""")

        for varname in pindict:
            main_cpp.append(f"    rio->{varname} = 0;")
            main_cpp.append(f"    uint8_t last_{varname} = 0;")

        main_cpp.append("""
    rio->sysclk_in = 0;
    rio->eval();

    pthread_t sdl_thread;
    pthread_create(&sdl_thread, NULL, run, rio);

    int spi_counter = 0;
    int chart_counter = 0;
    int vcd_counter = 0;
    int vcd_change = 0;
    while (!contextp->gotFinish() && running == 1) {
        rio->sysclk_in = 1 - rio->sysclk_in;
        rio->eval();
        rio->sysclk_in = 1 - rio->sysclk_in;
        rio->eval();

        if (vcd_record == 1 && vcd_running == 0) {
            printf("INFO: starting vcd_record to: /dev/shm/verilator.gtkw\\n");
            vcd_running = 1;
            vcd_counter = 0;
            fd_gtkw = fopen("/dev/shm/verilator.gtkw", "w");
            fprintf(fd_gtkw, "[*]\\n");
            fprintf(fd_gtkw, "[*] GTKWave Analyzer v3.3.118 (w)1999-2023 BSI\\n");
            fprintf(fd_gtkw, "[*] Wed Jul 15 10:04:27 2026\\n");
            fprintf(fd_gtkw, "[*]\\n");
            fprintf(fd_gtkw, "[dumpfile] \\"verilator.vcd\\"\\n");
            fprintf(fd_gtkw, "[dumpfile_mtime] \\"Wed Jul 15 10:03:02 2026\\"\\n");
            fprintf(fd_gtkw, "[savefile] \\"verilator.gtkwave.gtkw\\"\\n");
            fprintf(fd_gtkw, "[timestart] 0\\n");""")
        for varname in pindict:
            main_cpp.append(f'            fprintf(fd_gtkw, "testb_toggle.{varname}\\n");')

        main_cpp.append("""            fclose(fd_gtkw);

            fd_vcd = fopen("/dev/shm/verilator.vcd", "w");
            fprintf(fd_vcd, "$date\\n");
            fprintf(fd_vcd, "	Wed Jul 15 11:08:45 2026\\n");
            fprintf(fd_vcd, "$end\\n");
            fprintf(fd_vcd, "$version\\n");
            fprintf(fd_vcd, "	Icarus Verilog\\n");
            fprintf(fd_vcd, "$end\\n");
            fprintf(fd_vcd, "$timescale\\n");
            fprintf(fd_vcd, "	100ps\\n");
            fprintf(fd_vcd, "$end\\n");""")

        for cn, varname in enumerate(pindict):
            main_cpp.append('            fprintf(fd_vcd, "$scope module testb_toggle $end\\n");')
            main_cpp.append(f'            fprintf(fd_vcd, "$var wire 1 {chr(cn + 60)} {varname} $end\\n");')
            main_cpp.append('            fprintf(fd_vcd, "$upscope $end\\n");')
        main_cpp.append('            fprintf(fd_vcd, "$enddefinitions $end\\n");')
        main_cpp.append('            fprintf(fd_vcd, "#0\\n");')
        main_cpp.append('            fprintf(fd_vcd, "$dumpvars\\n");')
        for cn, varname in enumerate(pindict):
            main_cpp.append(f'            fprintf(fd_vcd, "%i{chr(cn + 60)}\\n", rio->{varname});')
        main_cpp.append('            fprintf(fd_vcd, "$end\\n");')
        main_cpp.append("""        }

        if (vcd_running == 1) {
            vcd_change = 0;
""")

        for cn, varname in enumerate(pindict):
            main_cpp.append(f"            if (last_{varname} != rio->{varname}) {{")
            main_cpp.append("                vcd_change = 1;")
            main_cpp.append("            }")

        main_cpp.append("            if (vcd_change == 1) {")
        main_cpp.append('                fprintf(fd_vcd, "#%i\\n", vcd_counter);')
        for cn, varname in enumerate(pindict):
            main_cpp.append(f"                if (last_{varname} != rio->{varname}) {{")
            main_cpp.append(f'                    fprintf(fd_vcd, "%i{chr(cn + 60)}\\n", rio->{varname});')
            main_cpp.append(f"                    last_{varname} = rio->{varname};")
            main_cpp.append("                }")

        main_cpp.append("""
            }
            vcd_counter++;
        }

        if (chart_counter++ > 100000) {
            chart_counter = 0;
""")

        for varname in pindict:
            main_cpp.append("            for (int i = 0; i < GRAPH_W - 1; i++) {")
            main_cpp.append(f"                hist_{varname.lower()}[i] = hist_{varname.lower()}[i + 1];")
            main_cpp.append("            }")
            main_cpp.append(f"            hist_{varname.lower()}[GRAPH_W - 1] = rio->{varname};")

        main_cpp.append("""
        }
        if (vcd_record == 0 && vcd_running == 1) {
            printf("INFO: stopping vcd_record\\n");
            vcd_running = 0;
            fclose(fd_vcd);
        }
#ifdef SPI_MOSI
        if (spi_counter++ > 1000) {
            spi_counter = 0;
            if (SPI_SEL == 0) {
                if (SPI_SCLK == 0) {
                    if (spi_rx_bit < 8) {
                        if ((spi_tx[spi_rx_num] & (1<<(7-spi_rx_bit))) > 0) {
                            SPI_MOSI = 1;
                        } else {
                            SPI_MOSI = 0;
                        }
                    }
                    SPI_SCLK = 1;
                } else if (spi_rx_num < BUFFER_BYTES) {
                    if (spi_rx_bit < 8) {
                        if (SPI_MISO == 1) {
                            spi_rx[spi_rx_num] |= (1<<(7-spi_rx_bit));
                        }
                        spi_rx_bit++;
                        if (spi_rx_bit == 8) {
                            spi_rx_bit = 0;
                            spi_rx_num++;
                            if (spi_rx_num == BUFFER_BYTES) {
                                int fd_rx = open("/dev/shm/verilator.rx", O_WRONLY | O_CREAT, 0644);
                                if (fd_rx < 0) {
                                    printf("ERROR open file: /dev/shm/verilator.rx: %i\\n", fd_rx);
                                } else {
                                    write(fd_rx, spi_rx, BUFFER_BYTES);
                                    close(fd_rx);
                                }
                            } else {
                                spi_rx[spi_rx_num] = 0;
                            }
                        }
                    }
                    if (spi_rx_num < BUFFER_BYTES) {
                        SPI_SCLK = 0;
                    }
                } else {
                    SPI_SEL = 1;
                    spi_rx_bit = 0;
                    spi_rx_num = 0;
                }
            } else if (SPI_SEL == 1) {
                int fd_tx = open("/dev/shm/verilator.tx", O_RDONLY);
                if (fd_tx < 0) {
                    // printf("ERROR open file: /dev/shm/verilator.tx\\n");
                } else {
                    read(fd_tx, spi_tx, BUFFER_BYTES);
                    close(fd_tx);
                }
                spi_rx_bit = 0;
                spi_rx_num = 0;
                spi_rx[spi_rx_num] = 0;
                SPI_SEL = 0;
                SPI_SCLK = 0;
            }
        }
#endif

    }
    running = 0;
    if (vcd_running == 1) {
        printf("INFO: stopping vcd_record\\n");
        fclose(fd_vcd);
    }
    delete rio;
    delete contextp;
    return 0;
}

""")
        open(os.path.join(path, "main.cpp"), "w").write("\n".join(main_cpp))
