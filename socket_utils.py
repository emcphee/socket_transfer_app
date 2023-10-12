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
                print(k,v[0])

        else:
            send_instant_message(message, SEND_queue)

def receive_chunks(socket, FILE_queue, IM_queue, current_downloading_files):
    while True:
        data = socket.recv(1024)
        decoded = data.decode()

        if decoded == '':
            break

        if decoded[0] == 'M': # M is for an instant message
            IM_queue.put(data[1:])

        elif decoded[0] == 'I': # I is for initial file chunk. It contains the name and size of the file seperated by a comma.
            name,size =  decoded[1:].split(',')
            current_downloading_files[name] = (int(size), open(name, "wb"))

        elif decoded[0] == 'F': # F is for any file chunks after the initial (content containing chunks)
            filename = decoded[1:64].rstrip('\n')
            FILE_queue.put( (filename, data[64:]) )
        
        else:
            print(f"Bad Chunk Recevied")

def send_chunks(socket, SEND_queue):
    while True:
        chunk = SEND_queue.get()
        socket.send(chunk)

def send_instant_message(message, SEND_queue):
    header = 'M'
    chunk = (header + message).ljust(1024, '\n')
    SEND_queue.put(chunk.encode())

def process_instant_messages(IM_queue):
    while True:
        data = IM_queue.get()
        newline = '\n'
        print(f"Received Message: {data.decode().rstrip(newline)}")

def send_initial_file_chunk(filesize, filename, SEND_queue):
    header = 'I'
    chunk = (header + filename + ',' + str(filesize)).ljust(1024, '\n')
    SEND_queue.put(chunk.encode())

def send_file(filename, SEND_queue):
    header = 'F'
    chunk = (header + filename).ljust(64, '\n')

    with open(filename, 'rb') as file:
        data = file.read(960).decode()  # Read and send the file in chunks of 960 bytes
        while data:
            #print(f"Bytes Remaining for {filename}: {bytes_remaining}")
            next_chunk = ((chunk + data).rjust(1024, '\n')).encode()
            
            SEND_queue.put(next_chunk)
            
            #time.sleep(0.01) # For some reason, not sleeping here causes chunks to be send incorrectly

            data = file.read(960).decode()
    print(f"Successfully sent file: {filename}")

def process_file_content(FILE_queue, current_downloading_files):
    while True:
        filename,data = FILE_queue.get()
        data = (data.decode().rstrip('\n')).encode()
        
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