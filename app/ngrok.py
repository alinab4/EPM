# app/ngrok.py
import os
from pyngrok import ngrok
from dotenv import load_dotenv

load_dotenv()

def init_ngrok():
    """Initializes ngrok and exposes the local server."""
    port = int(os.getenv("PORT", "8000"))
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    
    if not authtoken or authtoken == "YOUR_NGROK_AUTHTOKEN_HERE":
        print("✗ Ngrok authtoken not configured. Skipping ngrok initialization.")
        print("  Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
        return None
    
    try:
        ngrok.set_auth_token(authtoken)
        public_url = ngrok.connect(port)
        print(f"✓ Ngrok tunnel is active: {public_url}")
        print(f"  * Public URL: {public_url}")
        print(f"  * Local URL: http://127.0.0.1:{port}")
        return public_url
    except Exception as e:
        print(f"✗ Error initializing ngrok: {str(e)}")
        return None

def shutdown_ngrok():
    """Shuts down all active ngrok tunnels."""
    try:
        tunnels = ngrok.get_tunnels()
        if tunnels:
            for tunnel in tunnels:
                ngrok.disconnect(tunnel.public_url)
            print("✓ Ngrok tunnels closed successfully.")
    except Exception as e:
        print(f"✗ Error shutting down ngrok: {str(e)}")

