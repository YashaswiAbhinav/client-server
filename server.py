import socket
import threading
import os

# Use the PORT environment variable if available, otherwise default to 12345.
PORT = int(os.environ.get("PORT", 12345))
HOST = '0.0.0.0'  # Listen on all available interfaces

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

clients = []
clients_lock = threading.Lock()

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    with clients_lock:
        clients.append(client_socket)
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"[DISCONNECTED] {client_address} left the chat.")
                break
            print(f"[{client_address}] {message}")
            # Broadcast the message to all other clients (append newline so clients can read it properly)
            with clients_lock:
                for client in clients:
                    if client != client_socket:
                        try:
                            client.sendall(f"[{client_address}] {message}\n".encode('utf-8'))
                        except Exception as e:
                            print(f"[ERROR] Could not send message to {client.getpeername()}: {e}")
    except Exception as e:
        print(f"[ERROR] {client_address}: {e}")
    finally:
        with clients_lock:
            clients.remove(client_socket)
        client_socket.close()

print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()
