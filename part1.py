import sys
import socket

class client(object):
    """
    Class for describing simple HTTP clients objects
    """
    def __init__(self, url, redirect_count):
        self.url = url
        self.redirect_count = redirect_count

    def getpath(self):
        """
        Get path, hostname and port
        :return: filepath, host, port
        """
        a, b = self.url.split('://')[0], self.url.split('://')[1]
        # if not started with http, return error code 1
        if a != 'http':
            print("Error: url not started with http", file=sys.stderr)
            sys.exit(1)
        url = b.split('/')
        host = url[0]
        path = '/' + '/'.join(url[1:])
        # if exists particular port retrieve it, if not, set 80
        portlist = b.split(":")
        if len(portlist) != 1:
            port = int(portlist[1].split("/")[0])
            host = portlist[0]
        else:
            port = 80
        return path, host, port

    def start(self):
        """
        Attempts to create and bind a socket to launch the server
        :return:
        """
        path, host, port = self.getpath()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
        s.connect((host, port))
        sendmsg = "GET " + path + " HTTP/1.0\r\nHost: " + host + "\r\n\r\n"
        s.sendall(bytes(sendmsg, encoding="utf-8"))
        buff = ''
        while True:
            data_tmp = s.recv(4096)  # 收到server返回的html
            data_tmp = data_tmp.decode('utf-8', 'ignore')
            buff += data_tmp
            if data_tmp == '': break
        data = buff.split("\r\n")
        htmlbegin = 0
        for i in range(len(data)):
            if data[i].split(': ')[0] == 'Content-Type':
                htmlbegin = i + 2
                break
        for i in range(htmlbegin, len(data)):
            print(data[i], end='\n')
        status = data[0].split(' ')[1]
        if status == '200':  # succeed
            sys.exit(0)
        if status == '301' or '302':  # need redirect
            for i in data:
                if i.split(': ')[0] == 'Location':
                    location = i.split(": ")[1]
                    print("Redirect to: " + location, file=sys.stderr)
                    self.redirect_count += 1
                    if self.redirect_count > 10:  # 如果redirect的次数大于10需要返回错误代码2
                        print("Error: redirect too many times", file=sys.stderr)
                        sys.exit(2)
                    redirect_s = client(location, self.redirect_count)
                    redirect_s.start()
        if int(status) >= 400:  # not found
            # print("Error: Page not found", file=sys.stderr)
            sys.exit(3)
        s.close()


if __name__ == '__main__':
    hostname = sys.argv[1]
    redirect_count = 0
    s = client(hostname, redirect_count)
    s.start()