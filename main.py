from client_socket import ClientSocket
from server_socket import ServerSocket

# NOTES:
# IM's are assumed to be of length 1024 or less (could fix this)

# File transfers occur whenever a message starts with "/sendfile " and after the command the next arg is expected to be the file name 
# File names cannot exceed 63 characters.


ServerSocket('127.0.0.1', 8888)
#ClientSocket('127.0.0.1', 8888)
