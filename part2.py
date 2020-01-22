import sys
import socket
import time
import os

class WebServer(object):
    """
    Class for describing simple HTTP server objects
    """

    def __init__(self, port):
        self.host = 'localhost'
        self.port = port
        self.file_path = './'

    def start(self):
        """
        Attempts to create and bind a socket to launch the server
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print("Starting server on {host}:{port}".format(host=self.host, port=self.port))
            self.socket.bind((self.host, self.port))
            print("Server started on port {port}.".format(port=self.port))

        except Exception as e:
            print("Error: Could not bind to port {port}".format(port=self.port))
            sys.exit(1)

        self._listen() # Start listening for connections


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
                      'Content-Type: text/html; charset=UTF-8\n\n'
        elif response_code == 404:
            header += 'HTTP/1.0 404 Not Found\n' + \
                      'Date: {now}\n'.format(now=time_now) + \
                      'Server: Simple-Python-Server\n' + \
                      'Content-Length: {length}\n'.format(length=self.content_length) + \
                      'Connection: close\n' + \
                      'Content-Type: text/html; charset=UTF-8\n\n'
        elif response_code == 403:
            header += 'HTTP/1.0 403 Forbidden\n' + \
                      'Date: {now}\n'.format(now=time_now) + \
                      'Server: Simple-Python-Server\n' + \
                      'Content-Length: {length}\n'.format(length=self.content_length) + \
                      'Connection: close\n' + \
                      'Content-Type: text/html; charset=UTF-8\n\n'

        return header

    def _listen(self):
        """
        Listens on self.port for any incoming connections
        """
        self.socket.listen(5)
        while True:
            (client, address) = self.socket.accept()
            client.settimeout(60)
            print("Recieved connection from {addr}".format(addr=address))
            self._handle_client(client, address)


    def _handle_client(self, client, address):
        """
        Main loop for handling connecting clients and serving files from content_dir
        Parameters:
            - client: socket client from accept()
            - address: socket address from accept()
        """
        PACKET_SIZE = 4096
        while True:
            print("CLIENT", client)
            data = client.recv(PACKET_SIZE).decode()  # Recieve data packet from client and decode

            if not data:
                break

            request_method = data.split(' ')[0]
            print("Method: {m}".format(m=request_method))
            print("Request Body: {b}".format(b=data))

            if request_method == "GET":
                # Ex) "GET /index.html" split on space
                self.file_requested = data.split(' ')[1]
                print(self.file_requested)

                filepath_to_serve = '.' + self.file_requested
                filename = self.file_requested.split('.')[0][1:]
                print(self.file_requested)
                print(filename)
                ff = os.listdir(self.file_path)
                print(ff)
                print("Serving web page [{fp}]".format(fp=filepath_to_serve))
                for i in ff:
                    print(i)
                    if i.split('.')[0] == filename:
                        print('A')
                        if i.split('.')[1] == 'html' or i.split('.')[1] == 'htm':
                            f = open('./' + i, 'rb')
                            self.response_data = f.read()
                            self.response_data = self.response_data.decode()
                            self.content_length = len(self.response_data)
                            f.close()
                            response_header = self._generate_headers(200)
                        else:
                            print("File forbidden. Serving 403 page.", file=sys.stderr)
                            self.response_data = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n' + \
                                                 '<html><head>\n' + \
                                                 '<title>404 Not Found</title>\n' + \
                                                 '</head><body>\n' + \
                                                 '<h1>Not Found</h1>\n' + \
                                                 '<p>The requested URL {} was not found on this server.</p>\n'.format(
                                                     self.file_requested) + \
                                                 '</body></html>\n\n'
                            self.content_length = len(self.response_data)
                            response_header = self._generate_headers(403)
                        break
                else:
                    print("File not found. Serving 404 page.", file=sys.stderr)
                    self.response_data = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n' + \
                                         '<html><head>\n' + \
                                         '<title>403 Forbidden</title>\n' + \
                                         '</head><body>\n' + \
                                         '<h1>Forbidden</h1>\n' + \
                                         '<p>The requested URL {} was forbidden on this server.</p>\n'.format(
                                             self.file_requested) + \
                                         '</body></html>\n\n'
                    self.content_length = len(self.response_data)
                    response_header = self._generate_headers(404)


                response = response_header
                response += self.response_data
                response = response.encode()

                client.send(response)
                client.close()
                break
            else:
                print("Unknown HTTP request method: {method}".format(method=request_method))


if __name__ == "__main__":
    port = int(sys.argv[1])
    server = WebServer(port)
    server.start()
    print("Press Ctrl+C to shut down server.")