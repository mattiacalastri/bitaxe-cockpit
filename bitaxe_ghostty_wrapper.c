// Bitaxe Cockpit — Ghostty wrapper (Mach-O native macOS arm64)
//
// Launches the Bitaxe Cockpit TUI inside a dedicated Ghostty window
// (fullscreen, no save-state, fixed font-size) so it can be installed
// as a standalone macOS .app via standard bundling.
//
// Compile:
//     clang -O2 -arch arm64 -o ghostty bitaxe_ghostty_wrapper.c
//
// Configuration (env vars at run time):
//     BITAXE_COCKPIT_SCRIPT  Path to bitaxe_cockpit.py
//                            Default: <wrapper_dir>/bitaxe_cockpit.py
//     BITAXE_PYTHON          Python interpreter
//                            Default: /opt/homebrew/bin/python3.10
//
// MIT License — see LICENSE file in repo root.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libgen.h>
#include <mach-o/dyld.h>

int main(int argc, char *argv[]) {
    (void)argc; (void)argv;

    char exec_path[4096];
    uint32_t size = sizeof(exec_path);
    if (_NSGetExecutablePath(exec_path, &size) != 0) {
        fprintf(stderr, "bitaxe-cockpit: cannot resolve executable path\n");
        return 1;
    }

    char dir_buf[4096];
    strncpy(dir_buf, exec_path, sizeof(dir_buf) - 1);
    dir_buf[sizeof(dir_buf) - 1] = '\0';
    char *dir = dirname(dir_buf);

    char ghostty_bin[4096];
    snprintf(ghostty_bin, sizeof(ghostty_bin), "%s/ghostty.bin", dir);

    // Resolve Python interpreter
    const char *python = getenv("BITAXE_PYTHON");
    if (!python || !*python) python = "/opt/homebrew/bin/python3.10";

    // Resolve cockpit script
    const char *script = getenv("BITAXE_COCKPIT_SCRIPT");
    char script_default[4096];
    if (!script || !*script) {
        snprintf(script_default, sizeof(script_default), "%s/bitaxe_cockpit.py", dir);
        script = script_default;
    }

    char command_arg[8192];
    snprintf(command_arg, sizeof(command_arg), "--command=%s %s", python, script);

    char *new_argv[] = {
        ghostty_bin,
        "--title=Bitaxe Cockpit",
        "--fullscreen=true",
        "--class=org.bitaxe.cockpit",
        "--window-width=180",
        "--window-height=80",
        "--font-size=15",
        "--window-save-state=never",
        command_arg,
        NULL
    };

    execv(ghostty_bin, new_argv);
    perror("bitaxe-cockpit: execv ghostty.bin failed");
    return 1;
}
