import socket
import os
import threading

def create_threads(socket, FILE_queue, IM_queue, current_downloading_files):

        receive_chunks_thread = threading.Thread(target=receive_chunks, args=(socket, FILE_queue, IM_queue, current_downloading_files))
        process_instant_messages_thread = threading.Thread(target=process_instant_messages, args=(IM_queue,))
        read_user_input_thread = threading.Thread(target=read_user_input, args=(socket,))
        process_file_content_thread = threading.Thread(target=process_file_content, args=(FILE_queue,current_downloading_files))

        receive_chunks_thread.start()
        process_instant_messages_thread.start()
        read_user_input_thread.start()
        process_file_content_thread.start()

        receive_chunks_thread.join()
        process_instant_messages_thread.join()
        read_user_input_thread.join()
        process_file_content_thread.join()

def read_user_input(socket):
    while True:
        message = input()
        if message.startswith("/sendfile"):
            filename = message[10:]
            filesize = os.path.getsize(filename)
            send_initial_file_chunk(socket, filesize, filename)

            # Create thread that will send the file chunk by chunk
            threading.Thread(target=send_file, args=(socket,filename)).start()

        else:
            send_instant_message(socket, message)

def receive_chunks(socket, FILE_queue, IM_queue, current_downloading_files):
    while True:
        data = socket.recv(1024)
        decoded = data.decode()

        if decoded[0] == 'M': # M is for an instant message
            print("(M)")
            IM_queue.put(data[1:])

        elif decoded[0] == 'I': # I is for initial file chunk. It contains the name and size of the file seperated by a comma.
            name,size =  decoded[1:].split(',')
            current_downloading_files[name] = (int(size), open(name, "wb"))
            print("(I)")

        elif decoded[0] == 'F': # F is for any file chunks after the initial (content containing chunks)
            print("(F)")
            filename = decoded[1:64].rstrip('\n')
            FILE_queue.put( (filename, data[64:]) )

def send_instant_message(socket, message):
    header = 'M'
    chunk = header + message
    socket.send(chunk.encode())

def process_instant_messages(IM_queue):
    while True:
        data = IM_queue.get()
        print(f"Received Message: {data.decode()}")

def send_initial_file_chunk(socket, filesize, filename):
    header = 'I'
    chunk = (header + filename + ',' + str(filesize)).ljust(1024, '\n')
    socket.send(chunk.encode())

def send_file(socket, filename):
    header = 'F'
    chunk = ((header + filename).ljust(64, '\n')).encode()

    bytes_remaining = os.path.getsize(filename)
    with open(filename, 'rb') as file:
        data = file.read(960)  # Read and send the file in chunks of 960 bytes
        while data:
            #print(f"Bytes Remaining for {filename}: {bytes_remaining}")
            next_chunk = chunk + data
            socket.send(next_chunk)
            data = file.read(960)
            bytes_remaining -= 960
    print(f"Successfully sent file: {filename}")

def process_file_content(FILE_queue, current_downloading_files):
    while True:
        filename,data = FILE_queue.get()
        
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