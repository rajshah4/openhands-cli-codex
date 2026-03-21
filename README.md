# OpenHands Codex Tools

This repository contains tools to run OpenHands CLI with native OpenAI Codex support via ChatGPT subscription.

## Files

1.  `openhands-codex`: The CLI runner script.
2.  `login.py`: Authentication helper.
3.  `README.md`: Setup instructions (this file).

## Quick Start

1.  **Clone this repo**:
    ```bash
    git clone https://github.com/rajshah4/openhands-cli-codex.git
    cd openhands-cli-codex
    ```

2.  **Install Dependencies**:
    You need `openhands-cli` and `openhands-sdk`.
    ```bash
    uv pip install openhands-ai authlib
    ```

3.  **Authenticate**:
    ```bash
    uv run login.py
    ```

4.  **Run**:
    ```bash
    uv run ./openhands-codex
    ```

## Prerequisites

*   **Python 3.10+**
*   **uv** (recommended for environment management)
*   **Docker** (required for OpenHands runtime)
*   **ChatGPT Subscription** (Plus, Pro, or Max)

## Installation

1.  **Clone this repo**:
    ```bash
    git clone https://github.com/rajshah4/openhands-cli-codex.git
    cd openhands-cli-codex
    ```

2.  **Set up the environment**:
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install openhands-ai authlib
    ```

## Configuration

Create or update `~/.openhands/config.toml` to specify the Codex model you want to use.

```toml
[llm]
model = "openai/gpt-5.2-codex"  # Or gpt-5.4-codex, gpt-5.3-codex-spark
api_key = "not-needed"
temperature = 0.0

[sandbox]
# Add your trusted project directories here
trusted_dirs = [ "/Users/yourname/Code/yourproject" ]

[llm.condenser]
model = "openai/gpt-5.3-instant"
api_key = "not-needed"
temperature = 0.1
```

## Scripts

This repo contains two helper scripts:

### Script 1: `login.py` (Authentication)
Handles the OAuth flow with ChatGPT.

### Script 2: `openhands-codex` (Runner)
Runs the OpenHands CLI with the necessary patches for native Codex support.

## Usage

### Step 1: Authenticate (One-time)

Run the login script. It will provide a URL to authenticate with your ChatGPT account.

```bash
uv run login.py
```

Follow the instructions in the terminal. Once successful, credentials are saved securely.

### Step 2: Run OpenHands

Use the `openhands-codex` runner script.

**From the installation directory:**
```bash
uv run ./openhands-codex -t "Create a snake game in python"
```

**From any directory (Global Access):**
1.  Update the shebang line in `openhands-codex` to point to the absolute path of your venv python (e.g., `#!/Users/username/Code/OpenHands-CLI/.venv/bin/python3`).
2.  Add an alias to your shell profile (`~/.zshrc`):
    ```bash
    alias openhands-codex="/path/to/OpenHands-CLI/openhands-codex"
    ```
3.  Reload shell (`source ~/.zshrc`).
4.  Run:
    ```bash
    openhands-codex -t "Task description"
    ```

## FAQ

### Q: Why do I see "litellm_proxy" in the output/name of the model?
**A:** This is just an internal label OpenHands uses for the connection. It does NOT mean you are running a local proxy server. The connection goes directly to OpenAI (`chatgpt.com`).

### Q: Can I use other models?
**A:** Yes. Edit `~/.openhands/config.toml` and change the `model` field to any Codex model your account supports (e.g., `openai/gpt-5.4-codex`). The script automatically detects "codex" in the name and applies the correct authentication.

### Q: What if I see `MCPTimeoutError`?
**A:** This relates to optional tool servers (like Tavily/Notion). You can usually ignore it or retry. It does not affect the core LLM functionality.
