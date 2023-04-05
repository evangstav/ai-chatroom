import socket
import threading
from contextlib import closing


import clients



# client = clients.ClaudeClient()
client = clients.ChatGPTClient()

def generate_auto_response(message):
    if client:
        return str(client.complete(message)) + "\n\n"
    else:
        message = message.lower()
        if "hello" in message:
            return "Hi! How can I help you?"
        elif "bye" in message:
            return "Goodbye! Have a nice day!"
        else:
            return "I'm not sure how to respond to that."



def handle_client(client_socket, client_address):
    """Handles a single client connection and processes its messages."""
    with closing(client_socket):
        print(f"[*] New connection from {client_address}")

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"{client_address}: {message}")

                auto_response = generate_auto_response(message)
                client_socket.send(auto_response.encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                break

        print(f"[*] Connection closed with {client_address}")

def main():
    """Runs the main server loop, listening for new connections."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server:
        try:
            server.bind(('0.0.0.0', 9999))
        except socket.error as e:
            print(f"Error binding to socket: {e}")
            return

        server.listen(5)
        print("[*] Listening on 0.0.0.0:9999")

        while True:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()

if __name__ == '__main__':
    main()
