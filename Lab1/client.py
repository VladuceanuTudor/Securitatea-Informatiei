import socket
import ssl

HOST = 'localhost'
PORT = 8443
CA_CERT = 'server.crt'

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations(CA_CERT)
context.minimum_version = ssl.TLSVersion.TLSv1_3

with socket.create_connection((HOST, PORT)) as sock:
    with context.wrap_socket(sock, server_hostname=HOST) as ssock:
        print(f"Connectat: {ssock.version()}")

        print(ssock.recv(1024).decode())
        nums = input("Enter numbers: ")
        ssock.send(nums.encode())
        print(ssock.recv(1024).decode())
