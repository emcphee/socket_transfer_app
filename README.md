# Bidirectional Socket Transfer and Messaging CLI Tool

This project allows bidirectional simultaneous file transfer and messaging between two devices at the socket layer. It provides a simple solution for exchanging files and messages between two machines.

## Usage

### Installation
1. Clone this repository to your local machine:

    ```
    git clone github.com/emcphee/socket_transfer_app
    ```

2. Navigate to the project directory:

    ```
    cd socket_transfer
    ```

### Running the Application
The application can be run in client or server mode. Follow the usage instructions below:

```
Usage: socket_transfer [options] <mode> <ip_address>

Options:
  -p, --port <port>  Specify the port to listen on (default is 8888)

Modes:
  client             Run the app in client mode
  server             Run the app in server mode

Examples:
  socket_transfer client 192.168.1.100            # Run the app in client mode on default port 8888
  socket_transfer server 192.168.1.100            # Run the app in server mode on default port 8888
  socket_transfer server -p 9090 192.168.1.100    # Run the app in server mode on port 9090
```

Follow these steps to run the application:

1. Determine the mode in which you want to run the application (`client` or `server`).
2. Determine which IP address you want to run the application on (ipv4, public or private address of the machine for the server, and the IP to connect to for the client)
3. Optionally, specify the port to listen on using the `-p` or `--port` option. The default port is 8888.

### Running Application Examples
Here are some example commands to run the application:

- Run the application in client mode on the default port (8888) with the server IP address 192.168.1.100:

    ```
    socket_transfer client 192.168.1.100
    ```

- Run the application in server mode on the default port (8888):

    ```
    socket_transfer server 192.168.1.100
    ```

- Run the application in server mode on port 9090 with the server IP address 192.168.1.100:

    ```
    socket_transfer server -p 9090 192.168.1.100
    ```

### Application Usage

#### Sending Messages and Files

The application supports sending both instant messages (IM) and files between the client and server. Follow the guidelines below to effectively utilize this feature:

- **Instant Messages (IM)**:
  - Messages can be sent without any prefix or with the `/sendfile` prefix.
  - Messages without the `/sendfile` prefix are treated as instant messages and can be up to 1024 characters long.
  - Simply type your message and press Enter to send it.

Example:
```
Hello, how are you?
```

- **Sending Files**:
  - To send a file, start your message with the `/sendfile` prefix followed by the name of the file you want to send (up to 63 characters).
  - Ensure that the specified file exists in the current directory.
  - The application will automatically identify the `/sendfile` prefix and interpret the following text as the filename to be sent.
  - The file will be sent to the other device once the message is sent.

Example:
```
/sendfile mydocument.pdf
```

### Example Usage

Here's an example of how to use the messaging and file transfer features:

1. **Sending an Instant Message**:
   - Type your message and press Enter.
   - Example: `Hello, how are you?`

2. **Sending a File**:
   - Start your message with the `/sendfile` prefix followed by the filename.
   - Example: `/sendfile mydocument.pdf`

3. **Receiving Messages and Files**:
   - Messages and file transfers received from the other device will be displayed in the application's interface.