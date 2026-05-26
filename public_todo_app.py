import socket
import sys
import threading
import time

from pyngrok import ngrok

import web_app


def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def start_server():
    server = web_app.HTTPServer((web_app.HOST, web_app.PORT), web_app.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main():
    if not is_port_open(web_app.HOST, web_app.PORT):
        server = start_server()
        print(f"Local server started at http://{web_app.HOST}:{web_app.PORT}")
    else:
        server = None
        print(f"Local server already running at http://{web_app.HOST}:{web_app.PORT}")

    tunnel = ngrok.connect(web_app.PORT, host_header="localhost")
    public_url = tunnel.public_url
    print(f"Public URL: {public_url}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        if server is not None:
            server.shutdown()
            server.server_close()
        ngrok.kill()


if __name__ == "__main__":
    main()
