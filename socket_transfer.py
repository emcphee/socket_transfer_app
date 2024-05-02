from client_socket import ClientSocket
from server_socket import ServerSocket
import sys

# NOTES:
# IM's are assumed to be of length 1024 or less

# File transfers occur whenever a message starts with "/sendfile " and after the command the next arg is expected to be the file name 
# File names cannot exceed 63 characters.

usage = """Usage: socket_transfer [options] <mode> <ip_address>

Options:
  -p, --port <port>  Specify the port to listen on (default is 8888)

Modes:
  client             Run the app in client mode
  server             Run the app in server mode

Examples:
  socket_transfer client 192.168.1.100            # Run the app in client mode on default port 8888
  socket_transfer server 192.168.1.100            # Run the app in server mode on default port 8888
  socket_transfer server -p 9090 192.168.1.100    # Run the app in server mode on port 9090"""

def main():
    
  # default arg values
  port = 8888
  mode = None
  ip_address = None

  # parse arguments
  if len(sys.argv) == 3:
    if sys.argv[1].lower() == "client" or sys.argv[1].lower() == "server":
      mode = sys.argv[1].lower()
  elif len(sys.argv) == 5:
    if sys.argv[1].lower() == "-p" or sys.argv[1].lower() == "--port":
      if sys.argv[2].isdigit():
        if sys.argv[3].lower() == "client" or sys.argv[3].lower() == "server":
          mode = sys.argv[3].lower()
          port = int(sys.argv[2])
  
  if sys.argv[len(sys.argv) - 1].count(".") == 3:  # Simple check for IPv4 address
      ip_address = sys.argv[len(sys.argv) - 1]

  # if mode is not set, then the args were not valid
  if mode == None or ip_address == None:
    print(usage)
    exit(0)

  if mode == "server":
    ServerSocket(ip_address, port)
  else:
    ClientSocket(ip_address, port)

if __name__ == "__main__":
    main()