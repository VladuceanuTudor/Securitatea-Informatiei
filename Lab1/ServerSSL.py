import socket
import ssl
import threading
from pathlib import Path
import select

LOCAL_HOST = 'localhost'
LOCAL_PORT = 8443
RESOURCE_DIRECTORY = Path(__file__).resolve().parent 
SERVER_CERT_CHAIN = RESOURCE_DIRECTORY / 'server.crt'
SERVER_KEY = RESOURCE_DIRECTORY / 'server.key'


class SSLServer:
   
    def __init__(self):
       
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(certfile=SERVER_CERT_CHAIN, keyfile=SERVER_KEY)
        context.set_ciphers('AES128-SHA')
        self.context = context

    def start_server(self):
        
        server_socket = socket.socket()
        server_socket.bind((LOCAL_HOST, LOCAL_PORT))
        server_socket.listen(5)
        read_list = [server_socket]

        print("Listening on port {0}...".format(LOCAL_PORT))

        while True:
            client_socket, address = server_socket.accept()
            try:
                conn = self.context.wrap_socket(client_socket, server_side=True)
                ClientHandler(conn).start()
            except ssl.SSLError as e:
                print(e)
            


class ClientHandler(threading.Thread):
    
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        try:
            
            client_request = self.conn.recv(1024)
            print("Received from client:", client_request)
            
	
            self.conn.send(client_request)

            
            
        except ssl.SSLError as e:
            print(e)
        except Exception as e:
            print(e)
        finally:
            self.conn.close()


def main():
    server = SSLServer()
    server.start_server()


if __name__ == '__main__':
    main()
