import os
import socket
import time
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000
INPUT_FILE = 'input.txt'
OUTPUT_DIR = 'output'
CHECK_INTERVAL = 2
DISCONNECT_MESSAGE = "!DISCONNECT"
downloaded_files = set()

def download_file(client_socket, file_name):
    client_socket.sendall(file_name.encode())
    response = client_socket.recv(1024).decode()

    if response.startswith('OK'):
        file_size = int(response.split()[1])
        output_path = os.path.join(OUTPUT_DIR, file_name)
        with open(output_path, 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                bytes_received += len(data)
                # Tính toán và hiển thị phần trăm
                percent_complete = (bytes_received / file_size) * 100
                print(f"\rDownloading {file_name} ... {percent_complete:.2f}%", end='')
        print(f'\nFinished downloading {file_name}')
    else:
        print(f'File {file_name} not found on server')

def monitor_input_file(client_socket):
    while True:
        with open(INPUT_FILE, 'r') as f:
            files_to_download = [line.strip() for line in f.readlines() if line.strip() not in downloaded_files]

        for file_name in files_to_download:
            download_file(client_socket, file_name)
            downloaded_files.add(file_name)

        time.sleep(CHECK_INTERVAL)

def start_client():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Nhận danh sách file từ server và hiển thị
    files_info = client_socket.recv(4096).decode()
    print('Available files to download:')
    print(files_info)

    # Bắt đầu theo dõi file input.txt
    try:
        monitor_thread = threading.Thread(target=monitor_input_file, args=(client_socket,))
        monitor_thread.start()
        monitor_thread.join()
    except KeyboardInterrupt:
        print('Closing connection...')
        client_socket.sendall(DISCONNECT_MESSAGE.encode())  # Gửi tin nhắn ngắt kết nối
    finally:
        client_socket.close()  # Đảm bảo đóng socket trong mọi trường hợp

if __name__ == "__main__":
    start_client()
