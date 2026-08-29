FROM docker.io/cloudflare/sandbox:0.12.9-python

# GitHub #73 was preregistered on CPython 3.12. The stable Sandbox Python
# image currently ships 3.11, so install a managed 3.12 interpreter explicitly.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && /root/.local/bin/uv python install 3.12

# uv installs versioned Python executables into ~/.local/bin by default.
ENV PATH="/root/.local/bin:${PATH}"

RUN python3.12 -c 'import sys; assert sys.version_info[:2] == (3, 12)' \
    && git --version

# Keep Cloudflare's Sandbox ENTRYPOINT unchanged.
