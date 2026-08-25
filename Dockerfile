FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

ENV UV_NO_DEV=1
# Potential production optimization
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

# Dependencies rarely change, so copy seperately from the rest of the code
# Then it can cache and build faster
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Specific thing called "cache mount" used to improve performance across builds
# Can be used to replace the two COPY and RUN lines above to avoid having redundant temporary build files in the resulting docker image
# RUN --mount=type=cache,target=/root/.cache/uv \
#     --mount=type=bind,source=uv.lock,target=uv.lock \
#     --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
#     uv sync --locked --no-install-project

# Copy the rest of the files after installing dependencies
COPY . /app

# Run bot after build
CMD ["uv", "run", "main.py"]
