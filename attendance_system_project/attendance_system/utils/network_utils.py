import socket

def is_connected(hostname="8.8.8.8", port=53, timeout=3) -> bool:
    """
    Check if there's an internet connection by trying to connect to Google's DNS
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((hostname, port))
        return True
    except socket.error:
        return False