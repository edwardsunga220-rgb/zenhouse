import socket

def get_local_ip():
    """Detects the computer's IP address on the local network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect, just determines the route
        s.connect(('8.8.8.8', 1)) 
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def network_info(request):
    """Makes the IP address available in all HTML templates."""
    ip = get_local_ip()
    port = request.META.get('SERVER_PORT', '8000')
    base_url = f"http://{ip}:{port}"
    return {
        'local_ip': ip,
        'local_url': base_url
    }