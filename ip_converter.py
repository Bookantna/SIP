import socket 

def ip_to_chunk(ip):
    return socket.inet_aton(ip)

# Function to convert chunk back to IP
def chunk_to_ip(chunk):
    return socket.inet_ntoa(chunk)