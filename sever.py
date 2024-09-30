import os
import socket
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000
FILE_LIST = 'files.txt'

def handle_client(client_socket):
    with client_socket:
        # Gửi danh sách file cho client
        with open(FILE_LIST, 'r') as f:
            files_info = f.read()
        client_socket.sendall(files_info.encode())

        while True:
            file_name = client_socket.recv(1024).decode()
            if not file_name:
                break

            file_path = os.path.join('server_files', file_name)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                client_socket.sendall(f'OK {file_size}'.encode())

                with open(file_path, 'rb') as f:
                    bytes_sent = 0
                    while bytes_sent < file_size:
                        data = f.read(1024)
                        if not data:
                            break
                        client_socket.sendall(data)
                        bytes_sent += len(data)
            else:
                client_socket.sendall('NOT_FOUND'.encode())

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f'Server started at {HOST}:{PORT}')
    while True:
        client_socket, client_address = server.accept()
        print(f'Accepted connection from {client_address}')
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
