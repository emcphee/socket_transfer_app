import socket
import os
import threading
import time

def create_threads(socket, FILE_queue, IM_queue, current_downloading_files, SEND_queue):

        receive_chunks_thread = threading.Thread(target=receive_chunks, args=(socket, FILE_queue, IM_queue, current_downloading_files))
        process_instant_messages_thread = threading.Thread(target=process_instant_messages, args=(IM_queue,))
        read_user_input_thread = threading.Thread(target=read_user_input, args=(current_downloading_files, SEND_queue))
        process_file_content_thread = threading.Thread(target=process_file_content, args=(FILE_queue,current_downloading_files))
        send_chunks_thread = threading.Thread(target=send_chunks, args=(socket,SEND_queue))

        receive_chunks_thread.start()
        process_instant_messages_thread.start()
        read_user_input_thread.start()
        process_file_content_thread.start()
        send_chunks_thread.start()

        receive_chunks_thread.join()
        process_instant_messages_thread.join()
        read_user_input_thread.join()
        process_file_content_thread.join()
        send_chunks_thread.join()

def read_user_input(current_downloading_files, SEND_queue):
    while True:
        message = input()
        if message.startswith("/sendfile"):
            filename = message[10:]
            filesize = os.path.getsize(filename)
            send_initial_file_chunk(filesize, filename, SEND_queue)

            # Create thread that will send the file chunk by chunk
            threading.Thread(target=send_file, args=(filename, SEND_queue)).start()
        
        elif message.startswith("/status"):
            for k,v in current_downloading_files.items():
                print(k,str(v[0] // 1024 // 1024) + "MB remaining")

        else:
            send_instant_message(message, SEND_queue)

def receive_chunks(socket, FILE_queue, IM_queue, current_downloading_files):
    while True:
        data = socket.recv(1024)

        try:
            header = data[:64].decode()
        except:
            print("Failed to decode header.")
            continue

        if not data:
            break

        if header[0] == 'M': # M is for an instant message
            IM_queue.put(data[1:])

        elif header[0] == 'I': # I is for initial file chunk. It contains the name and size of the file seperated by a comma.
            name,size =  header[1:].split(',')
            print(f"Starting to download {name}")
            current_downloading_files[name] = (int(size), open('downloads/' + name, "wb"))

        elif header[0] == 'F': # F is for any file chunks after the initial (content containing chunks)
            filename = header[1:].rstrip('\n')
            FILE_queue.put( (filename, data[64:]) )
        
        else:
            print(f"Bad Chunk Recevied")
        
        print(f"Received type: {header[0]}")
        

def send_chunks(socket, SEND_queue):
    while True:
        chunk = SEND_queue.get()

        print(f"Sending Chunk With Type: {chunk[0:1].decode()}")

        chunk_padded = chunk + bytearray(b'\n' * 1024 - len(chunk))
        socket.send(chunk_padded)

def send_instant_message(message, SEND_queue):
    header = 'M'
    chunk = header + message
    SEND_queue.put(chunk.encode())

def process_instant_messages(IM_queue):
    while True:
        data = IM_queue.get()
        newline = '\n'
        print(f"Received Message: {data.decode().rstrip(newline)}")

def send_initial_file_chunk(filesize, filename, SEND_queue):
    header = 'I'
    chunk = header + filename + ',' + str(filesize)
    SEND_queue.put(chunk.encode())

def send_file(filename, SEND_queue):
    header = ('F' + filename).ljust(64, '\n')

    with open(filename, 'rb') as file:
        while True:
            data = file.read(960)
            if not data:
                print(f"Successfully sent file: {filename}")
                break  # End of file

            chunk = header.encode() + data

            SEND_queue.put(chunk)

def process_file_content(FILE_queue, current_downloading_files):
    while True:
        filename,data = FILE_queue.get()
        data = data.rstrip(b'\n')
        
        res = current_downloading_files.get(filename)
        if res != None:
            bytes_remaining,fp = res
            fp.write(data)
            if bytes_remaining - 960 <= 0:
                fp.close()
                del current_downloading_files[filename]
                print(f"Successfully downloaded {filename}")
            else:
                current_downloading_files[filename] = (bytes_remaining - 960, fp)