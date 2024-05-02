from socket_utils import *
import socket
import os
import queue
import threading

class ClientSocket:
    def __init__(self, ip, port):
        # Create a socket and bind it to the provided ip and port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.server_address = (ip, port)

        # Threadsafe queues to put the received data
        self.IM_queue = queue.Queue()
        self.FILE_queue = queue.Queue()
        self.SEND_queue = queue.Queue()

        # Format should be: key=filename, value=remaining_bytes
        self.current_downloading_files = dict()
        
        self.attempt_connection()
    
    def attempt_connection(self):
        try:
            self.client_socket.connect(self.server_address)
            
            # SOCKET CONNECTION IS OPEN HERE
            create_threads(self.client_socket, self.FILE_queue, self.IM_queue, self.current_downloading_files, self.SEND_queue)

            print("Connection terminated.")

        except:
            print(f"Connection to {self.server_address[0]}:{self.server_address[1]} failed.")