import socket
import os
import threading
import time

# Creating all of the threads needed to operate the bidirection communiciation
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



# -- USER INPUT -- #

# Threaded while true loop to take in input and call functions or create threads needed
def read_user_input(current_downloading_files, SEND_queue):
    while True:
        message = input()
        if message.startswith("/sendfile"):
            filename = message[10:]
            if not os.path.exists(filename):
                print("File doesn't exist.")
                continue
            filesize = os.path.getsize(filename)
            send_initial_file_chunk(filesize, filename, SEND_queue)

            # Create thread that will send the file chunk by chunk
            threading.Thread(target=send_file, args=(filename, SEND_queue)).start()
        
        elif message.startswith("/status"):
            for k,v in current_downloading_files.items():
                print(k,str(v[0] // 1024) + "KB remaining")

        else:
            send_instant_message(message, SEND_queue)


# -- SOCKET COMMUNICATION -- #

# Threaded while true loop to send chunks whenever they are available in the SEND_queue
def send_chunks(socket, SEND_queue):
    while True:
        header,data = SEND_queue.get()

        if header[0] == 'M' or header[0] == 'I':
            chunk = header.ljust(64, '\n').encode()
    
        elif header[0] == 'F':
            chunk = header.ljust(64, '\n').encode() + data

        chunk_padded = chunk + b'\n' * (1024 - len(chunk))
        socket.send(chunk_padded)

# Threaded function to constantly read for chunks from the socket
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

        elif header[0] == 'I': # I is for initial file chunk. It contains the name and size of the file seperated by a comma
            name,size =  header[1:].split(',')
            print(f"Starting to download {name}")
            current_downloading_files[name] = (int(size), open('downloads/' + name, "wb"))

        elif header[0] == 'F': # F is for any file chunks after the initial (content containing chunks)
            filename = header[1:].rstrip('\n')
            FILE_queue.put( (filename, data[64:]) )
        
        else:
            print(f"Bad Chunk Recevied: header type = {header[0]}")




# -- ADDING TO SEND_queue -- #

# Adds a IM to the send queue
def send_instant_message(message, SEND_queue):
    header = 'M' + message
    SEND_queue.put( (header, None) )

# Adds an initial file chunk to the SEND_queue
def send_initial_file_chunk(filesize, filename, SEND_queue):
    header = 'I' + filename + ',' + str(filesize)
    SEND_queue.put( (header, None) )




# -- PROCESSING RECEIVED CHUNKS -- #

# Threaded while true loop to read out IMs from the IM queue to the console
def process_instant_messages(IM_queue):
    while True:
        data = IM_queue.get()
        newline = '\n'
        print(f"Received Message: {data.decode().rstrip(newline)}")

# Writes file chunks to the correct file pointer
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




# -- FILE SEND THREAD -- #

# This is a function which is created in a new thread for each new file send
# It opens, reads chunks of data from the file, and adds them, to the SEND_queue
def send_file(filename, SEND_queue):
    header = 'F' + filename

    with open(filename, 'rb') as file:
        while True:
            data = file.read(960)
            if not data:
                print(f"Successfully sent file: {filename}")
                break  # End of file

            SEND_queue.put( (header, data) )