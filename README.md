# OpenHands with OpenAI Codex (Native Support)

This guide explains how to set up the OpenHands CLI to run with OpenAI Codex models (`gpt-5.3-codex`, `gpt-5.4-codex`) using your **ChatGPT Plus/Pro/Max subscription**. This uses native device authentication (no API key billing required).

## 1. Prerequisites

*   **Python 3.10+**
*   **uv** (recommended for environment management)
*   **Docker** (required for OpenHands runtime)
*   **ChatGPT Subscription** (Plus, Pro, or Max)

## 2. Installation

1.  **Clone the OpenHands CLI repository**:
    ```bash
    git clone https://github.com/OpenHands/OpenHands-CLI.git
    cd OpenHands-CLI
    ```

2.  **Set up the environment**:
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -e . openhands-sdk authlib
    ```

## 3. Configuration

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

## 4. Setup Scripts

Create two helper scripts in your installation directory to handle authentication and running the CLI with native support.

### Script 1: `login.py` (Authentication)

Create a file named `login.py`:

```python
import asyncio
from openhands.sdk.llm.auth.openai import subscription_login_async

async def main():
    print("Starting subscription login...")
    try:
        # Triggers browser login flow
        llm = await subscription_login_async(model="gpt-5.2-codex", open_browser=False)
        print("Login successful!")
        if llm.api_key:
            print(f"Access Token: {llm.api_key.get_secret_value()[:10]}...")
            # Token is automatically saved to ~/.openhands/auth/
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Script 2: `openhands-codex` (Runner)

Create a file named `openhands-codex` with the following content. **Make sure to update the shebang line** to point to your virtual environment's python if you want to run it globally.

```python
#!/usr/bin/env python3
import sys
import json
import base64
import copy
from pathlib import Path
from openhands.llm import llm as llm_module
from openhands_cli.entrypoint import main
from openhands.core.config import LLMConfig
from pydantic import SecretStr

# Helper: Decode JWT
def decode_jwt_payload(token):
    try:
        parts = token.split(".")
        if len(parts) < 2: return {}
        payload = parts[1]
        padded = payload + "=" * (4 - len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return {}

# Load Credentials
creds_path = Path.home() / ".openhands/auth/openai_oauth.json"
if not creds_path.exists():
    print("Error: Credentials not found. Please run login.py first.")
    sys.exit(1)

with open(creds_path) as f:
    creds = json.load(f)
access_token = creds.get("access_token")
payload = decode_jwt_payload(access_token)
auth_info = payload.get("https://api.openai.com/auth", {})
account_id = auth_info.get("chatgpt_account_id")

# Helper: System Message Transformation
def transform_messages_for_codex(messages):
    msgs = copy.deepcopy(messages)
    system_chunks = []
    input_items = []
    
    for m in msgs:
        role = m.get("role")
        content = m.get("content")
        if role == "system":
            if isinstance(content, str): system_chunks.append(content)
            elif isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "text": system_chunks.append(b.get("text", ""))
        else:
            input_items.append(m)
            
    if system_chunks:
        merged = "\n\n---\n\n".join(system_chunks)
        prefix = {"type": "text", "text": f"Context (system prompt):\n{merged}\n\n"}
        if input_items and input_items[0].get("role") == "user":
            c = input_items[0].get("content")
            if isinstance(c, str): c = [{"type": "text", "text": c}]
            input_items[0]["content"] = [prefix] + (c if isinstance(c, list) else [])
        else:
            input_items.insert(0, {"role": "user", "content": [prefix]})
    return input_items

# Monkey Patch LLM
original_init = llm_module.LLM.__init__

def patched_init(self, config: LLMConfig, *args, **kwargs):
    if "codex" in config.model:
        config.api_key = SecretStr(access_token)
        config.base_url = "https://chatgpt.com/backend-api/codex" 
        
        extra_headers = {
            "originator": "codex_cli_rs",
            "OpenAI-Beta": "responses=experimental",
            "Authorization": f"Bearer {access_token}"
        }
        if account_id: extra_headers["chatgpt-account-id"] = account_id

        original_init(self, config, *args, **kwargs)
        
        original_completion = self._completion
        def wrapped_completion(*c_args, **c_kwargs):
            if "extra_headers" in c_kwargs: c_kwargs["extra_headers"].update(extra_headers)
            else: c_kwargs["extra_headers"] = extra_headers
            
            if "messages" in c_kwargs:
                c_kwargs["messages"] = transform_messages_for_codex(c_kwargs["messages"])
            c_kwargs["stream"] = True
            return original_completion(*c_args, **c_kwargs)
            
        self._completion = wrapped_completion
    else:
        original_init(self, config, *args, **kwargs)

llm_module.LLM.__init__ = patched_init

if __name__ == "__main__":
    sys.exit(main())
```

**Make it executable:**
```bash
chmod +x openhands-codex
```

## 5. Usage

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

## 6. FAQ

### Q: Why do I see "litellm_proxy" in the output/name of the model?
**A:** This is just an internal label OpenHands uses for the connection. It does NOT mean you are running a local proxy server. The connection goes directly to OpenAI (`chatgpt.com`).

### Q: Can I use other models?
**A:** Yes. Edit `~/.openhands/config.toml` and change the `model` field to any Codex model your account supports (e.g., `openai/gpt-5.4-codex`). The script automatically detects "codex" in the name and applies the correct authentication.

### Q: What if I see `MCPTimeoutError`?
**A:** This relates to optional tool servers (like Tavily/Notion). You can usually ignore it or retry. It does not affect the core LLM functionality.
