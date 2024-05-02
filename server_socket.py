from socket_utils import *
import queue
import threading
import socket
import os

class ServerSocket:
    def __init__(self, ip, port):
        # Create a socket and bind it to the provided ip and port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_address = (ip, port)
        self.server_socket.bind(self.server_address)

        # --- Here I define the variables that will be shared by the threads

        # Format should be: key=filename, value=remaining_bytes
        self.current_downloading_files = dict()

        # Threadsafe queues to put the received data
        self.IM_queue = queue.Queue()
        self.FILE_queue = queue.Queue()
        self.SEND_queue = queue.Queue()

        self.listen()
    
    def listen(self):
        # Listen for connections
        self.server_socket.listen(1)
        print(f"Server is listening on {self.server_address[0]}:{self.server_address[1]}")
        try:
            while True:
                print("Waiting for next client...")
                # Wait for the next connection here
                client_socket, client_address = self.server_socket.accept()
                print(f"Accepted connection from {client_address}")

                # CONNECTION IS OPEN HERE
                create_threads(client_socket, self.FILE_queue, self.IM_queue, self.current_downloading_files, self.SEND_queue)

        except KeyboardInterrupt:
            self.server_socket.close()
            return
