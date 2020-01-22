import sys
import socket
import time
import json

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
        self.content_length = 512
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
        elif response_code == 400:
            header += 'HTTP/1.0 400 Operand not number\n' + \
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

    def isfloat(self, number):
        try:
            float(number)
            return True
        except:
            return False


    def _handle_client(self, client, address):
        """
        Main loop for handling connecting clients and serving files from content_dir
        Parameters:
            - client: socket client from accept()
            - address: socket address from accept()
        """
        PACKET_SIZE = 4096
        buff = ''
        while True:
            data_tmp = client.recv(PACKET_SIZE)  # 收到server返回的html
            data_tmp = data_tmp.decode('utf-8', 'ignore')
            buff += data_tmp
            if data_tmp == '': break

            data = buff.split("\r\n")
            print(data)

            request_method = data[0].split(' ')[0]
            print("Method: {m}".format(m=request_method))
            print("Request Body: {b}".format(b=data))
            query = data[0].split(' ')[1]
            operation = query.split('?')[0]
            response_code = 200
            # not product, return 404
            if operation != '/product':
                response_code = 404
            tmp = query.split('?')[1].split('&')
            operand = []
            for i in tmp:
                tmp_operand = i.split('=')[1]
                # operand not digit, return 400
                if not self.isfloat(tmp_operand):
                    print(tmp_operand)
                    response_code = 400
                operand.append(float(i.split('=')[1]))
            result = 1
            for i in operand:
                result *= i
            response = self._generate_headers(response_code)
            answer = json.dumps({'operation': "product", 'operands': operand, 'result': result}, indent=4)
            if response_code == 200:
                response += answer
            response = response.encode()
            client.sendall(response)
            client.close()
            break


if __name__ == "__main__":
    port = int(sys.argv[1])
    server = WebServer(port)
    server.start()
    print("Press Ctrl+C to shut down server.")