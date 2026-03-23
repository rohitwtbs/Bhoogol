# Bhoogol
Voxel Engine (like Minecraft) in Python and OpenGL 

Control: WASDQE + mouse

![minecraft](/screenshot/0.jpg)

## WASM / Browser Build

A WebAssembly build lets you run Bhoogol in the browser using [Pygbag](https://pygame-web.github.io/).

### Quick start (Docker)

```bash
chmod +x build_wasm.sh
./build_wasm.sh
# → opens at http://localhost:8080
```

### Manual steps

```bash
# 1. Build the Docker image (compiles Python → WASM)
docker build -t bhoogol-wasm .

# 2. Run the server
docker run --rm -p 8080:8080 bhoogol-wasm

# 3. Open http://localhost:8080
```

### Local dev (no Docker)

```bash
pip install pygbag
python -m pygbag --ume_block 0 .
# → dev server at http://localhost:8000
```

### How it works

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage: Pygbag build → nginx serve |
| `main_web.py` | Async entry point for browser (becomes `main.py` in container) |
| `wasm_settings.py` | Smaller world/chunks for browser perf |
| `glm_shim.py` | Pure-Python PyGLM replacement |
| `opensimplex_shim.py` | Pure-Python noise when native ext unavailable |
| `shader_program.py` | Auto-patches shaders to GLSL ES 300 on Emscripten |

**Note:** The WASM build runs without numba JIT, so world generation is slower. The world size is reduced (4×2×4 chunks of 32³) to compensate.
