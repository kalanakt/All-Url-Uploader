import logging
import threading
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler

# === FORCE RENDER PORT BINDING ON BOOT ===
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), DummyHandler)
        logging.info(f"Dummy HTTP server listening on port {port}")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Failed to start dummy server: {e}")

# Run the port binding server on a dedicated background thread instantly
threading.Thread(target=run_dummy_server, daemon=True).start()
# =========================================

# Now let your original bot execution code load seamlessly below this line:
from main import main # (Or whatever command your setup uses to start long polling)

if __name__ == "__main__":
    asyncio.run(main())
