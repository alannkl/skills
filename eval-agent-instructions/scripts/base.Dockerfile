# Base image for every eval task: the agent CLIs preinstalled at pinned versions,
# so Harbor's install step finds them and per-trial setup stays within its timeout.
FROM ubuntu:24.04
ARG CLAUDE_CODE_VERSION
ARG CODEX_VERSION
ARG OPENCLAW_VERSION
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates git ripgrep procps bash \
    && rm -rf /var/lib/apt/lists/*
ENV NVM_DIR=/root/.nvm
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash \
    && . "$NVM_DIR/nvm.sh" && nvm install 24 && nvm alias default 24 \
    && npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
         "@openai/codex@${CODEX_VERSION}" "openclaw@${OPENCLAW_VERSION}" \
    && for bin in node npm npx claude codex openclaw; do ln -sf "$(command -v $bin)" /usr/local/bin/$bin; done \
    && claude --version && codex --version && openclaw --version
