import sys
import socket
import time
import select

# import signal # Allow socket destruction on Ctrl+C

"""
def shutdownServer(sig, unused):
    Shutsdown server from a SIGINT recieved signal
    server.shutdown()
    sys.exit(1)
"""


class WebServer(object):
    """
    Class for describing simple HTTP server objects
    """

    def __init__(self, port):
        self.host = 'localhost'
        self.port = port
        self.socket_list = []  # a list to put all the socket in
        self.server_socket = None

    def start_multiple(self):
        """
        Attempts to create and bind a socket to launch the server
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:

            self.server_socket.bind((self.host, self.port))
            self.server_socket.setblocking(0)
            self.server_socket.listen(5)
            print("Server started on port {port}.".format(port=self.port))
        except Exception as e:
            print("Error: Could not bind to port {port}".format(port=self.port))
            # self.shutdown()
            sys.exit(1)
        self._listen()  # Start listening for connections

    """
    def shutdown(self):
        try:
            print("Shutting down server")
            s.socket.shutdown(socket.SHUT_RDWR)

        except Exception as e:
            pass # Pass if socket is already closed
    """

    def _generate_headers(self, response_code):
        """
        Generate HTTP response headers.
        Parameters:
            - response_code: HTTP response code to add to the header. 200, 403 and 404 supported
        Returns:
            A formatted HTTP header for the given response_code
        """
        header = ''
        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        if response_code == 200:
            header += 'HTTP/1.0 200 OK\n' + \
                      'Date: {now}\n'.format(now=time_now) + \
                      'Server: Simple-Python-Server\n' + \
                      'Content-Length: {length}\n'.format(length=self.content_length) + \
                      'Connection: close\n' + \
                      'Content-Type: text/html; charset=UTF-8\n\n' + \
                      self.response_data.decode('utf-8') + '\n'
        elif response_code == 404:
            header += 'HTTP/1.0 404 Not Found\n' + \
                      'Date: {now}\n'.format(now=time_now) + \
                      'Server: Simple-Python-Server\n' + \
                      'Content-Length: {length}\n'.format(length=self.content_length) + \
                      'Connection: close\n' + \
                      'Content-Type: text/html; charset=UTF-8\n\n' + \
                      '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n' + \
                      '<html><head>\n' + \
                      '<title>404 Not Found</title>\n' + \
                      '</head><body>\n' + \
                      '<h1>Not Found</h1>\n' + \
                      '<p>The requested URL {} was not found on this server.</p>\n'.format(self.file_requested) + \
                      '</body></html>\n\n'
        elif response_code == 403:
            header += 'HTTP/1.0 403 Forbidden\n'

        return header

    def _listen(self):
        """
        Listens on self.port for any incoming connections
        """
        inputs = [self.server_socket]
        # outputs = []
        while True:
            # read_list, writable, exceptional = select.select(inputs, outputs, inputs)
            read_list, _, _ = select.select(inputs, [], [])
            for socket in read_list:
                if socket == self.server_socket:
                    # print()
                    client_socket, client_info = self.server_socket.accept()
                    client_socket.setblocking(0)
                    # client_socket.settimeout(60)
                    print(f"Client: {client_info} is connected.")
                    inputs.append(client_socket)
                else:
                    try:
                        self._handle_client(socket)
                        socket.close()
                        inputs.remove(socket)
                    except KeyboardInterrupt:
                        sys.stderr.write('Terminated by Ctrl + C\n')
                        sys.exit(1)
                    except:
                        # sys.stderr.write('error occured, please try again\n')
                        socket.close()
                        inputs.remove(socket)

    def _handle_client(self, client):
        """
        Main loop for handling connecting clients and serving files from content_dir
        Parameters:
            - client: socket client from accept()
            - address: socket address from accept()
        """
        PACKET_SIZE = 1024
        while True:
            print("CLIENT", client)
            data = client.recv(PACKET_SIZE).decode()  # Recieve data packet from client and decode

            # if not data:
            #     # if data received is empty, remove the client socket
            #     # client.close()
            #     # 从监听列表中删除该套接字
            #     # self.socket_list.remove(socket)
            #     break

            request_method = data.split(' ')[0]
            print("Method: {m}".format(m=request_method))
            print("Request Body: {b}".format(b=data))

            if request_method == "GET":
                # Ex) "GET /index.html" split on space
                self.file_requested = data.split(' ')[1]

                # if file_requested == "/":
                #    file_requested = "/index.html"

                filepath_to_serve = '.' + self.file_requested
                print("Serving web page [{fp}]".format(fp=filepath_to_serve))

                # Load and Serve files content
                try:
                    f = open(filepath_to_serve, 'rb')
                    self.response_data = f.read()
                    #print(self.response_data)
                    self.content_length = len(self.response_data)
                    f.close()
                    response_header = self._generate_headers(200)

                except Exception as e:
                    print("File not found. Serving 404 page.")
                    response_header = self._generate_headers(404)

                    if request_method == "GET":  # Temporary 404 Response Page
                        self.response_data = b"<h1>404 Not Found</h1>"

                response = response_header
                response += self.response_data
                response.encode()

                client.sendall(response)
                client.close()
                break
            else:
                print("Unknown HTTP request method: {method}".format(method=request_method))


if __name__ == "__main__":
    # signal.signal(signal.SIGINT, shutdownServer)
    port = sys.argv[1]
    #port = input()
    server = WebServer(int(port))
    server.start_multiple()
    print("Press Ctrl+C to shut down server.")
