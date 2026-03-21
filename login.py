import asyncio
from openhands.sdk.llm.auth.openai import subscription_login_async

async def main():
    print("Starting subscription login...")
    try:
        llm = await subscription_login_async(model="gpt-5.2-codex", open_browser=False)
        print("Login successful!")
        if llm.api_key:
            print(f"Access Token: {llm.api_key.get_secret_value()[:10]}...")
            # Token is automatically saved to ~/.openhands/auth/
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
