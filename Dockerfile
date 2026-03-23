# ── Stage 1: Build the WASM package with Pygbag ──────────────────────
FROM python:3.11-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pygbag

WORKDIR /src

# Copy project files
COPY main_web.py          main.py
COPY wasm_settings.py     wasm_settings.py
COPY settings.py          settings.py
COPY glm_shim.py          glm_shim.py
COPY opensimplex_shim.py  opensimplex_shim.py
COPY camera.py            camera.py
COPY frustum.py           frustum.py
COPY noise.py             noise.py
COPY player.py            player.py
COPY scene.py             scene.py
COPY shader_program.py    shader_program.py
COPY terrain_gen.py        terrain_gen.py
COPY textures.py          textures.py
COPY voxel_handler.py     voxel_handler.py
COPY world.py             world.py

COPY assets/              assets/
COPY meshes/              meshes/
COPY shaders/             shaders/
COPY world_objects/       world_objects/

# Pygbag expects the entry point to be named main.py in the project root.
# We already copied main_web.py → main.py above.

# Build the WASM bundle.
# --build  = build-only mode (no dev-server)
# --ume_block 0 = don't ask for user confirmation
RUN python -m pygbag --build --ume_block 0 /src

# ── Stage 2: Serve the built output with nginx ───────────────────────
FROM nginx:alpine

# Pygbag outputs the web build to build/web/ relative to the project dir
COPY --from=builder /src/build/web /usr/share/nginx/html

# Configure nginx for SPA-style serving + proper WASM MIME types
RUN echo 'server { \
    listen 8080; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    types { \
        application/wasm wasm; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
