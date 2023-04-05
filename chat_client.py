import socket
import threading

def receive_messages(sock):
    while True:
        message = sock.recv(1024).decode('utf-8')
        print(f"Server: {message}")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9999))

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        message = input("Enter message: ")
        client.send(message.encode('utf-8'))

if __name__ == '__main__':
    main()
