import socket, json, select

socket.setdefaulttimeout(0.1)
class Socket:
    #address = (ip, port)
    def __init__(self, address):
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.state = {}

        #[readers, writers]
        self.select_list = [[self.sock], [], []]
        self.read_buffer = {}
        self.write_buffer = {}

    def request(self, name, value):
        pass

    def apply(self, name, value):
        pass

    def send(self, message, target_sock=None):
        sock = target_sock if target_sock else self.sock

        if len(self.write_buffer.get(sock, "")):
            print("sent")
            sent = sock.send(self.write_buffer[s])
            self.write_buffer[s] = self.write_buffer[s][sent:]
 
    def recv(self, target_sock=None):
        sock = target_sock if target_sock else self.sock

        try:
            recv_string = sock.recv(1024).decode()
            print("recvd")
            if recv_string == b"":
                s.shutdown(socket.SHUT_RDWR)
                s.close()

                print("socket disconnected")

            self.read_buffer[sock] += recv_string

        except socket.timeout as e:
            if e.args[0] == "timed out":
                return 

    def process_data(self, socket):
        pass
    
    def readable_handler(self, socket):
        self.recv(socket)

    def writable_handler(self, socket):
        if len(self.write_buffer.get(socket, "")):
            self.send(socket)

    def event_handler(self):
        print("start event h")
        readables, writables, err = select.select(*self.select_list, 0)

        #read/recv
        for s in readables:
            print("start read")
            self.readable_handler(s)
            self.process_data(s)
            print("end read")
                    
        for s in writables:
            print("start write")
            self.writable_handler(s)
            print("end write")

        print("end event h")

#a server's job is only to generate server-side client sockets to chat up with connecting clients on the other side
class Server(Socket):
    def __init__(self, address):
        super().__init__(address)
        self.sock.bind(self.address)
        self.sock.listen(5)

    def process_data(self, sock):
        #data should be in the form of "r:var;w:var=value;"
        #r : read/get, w : write/set
        if sock != self.sock:

            if ";" in self.read_buffer.get(sock, ""):
                cmd_token = [i.strip() for i in self.read_buffer[sock].split(";")[-1]]
                protocol, data = [i.strip() for i in cmd_token.split(":")]
                if protocol == "r":
                    response_msg = f"{data}={self.state.get(data)};".encode()
                    self.write_buffer[sock] += response_msg

                elif protocol == "w":
                    data = [i.strip() for i in data.split("=")]
                    self.state[data[0]] = json.loads(data[1])


    def writable_handler(self, socket):
        super().__init__(socket)

    def event_handler(self):
        super().event_handler()

    def readable_handler(self, socket):
        if socket != self.sock:
            self.recv(socket)

        else:
            conn, address = self.sock.accept()
            self.select_list[0].append(conn)
            self.read_buffer[conn] = ""
            self.write_buffer[conn] = ""


class Client(Socket):
    def __init__(self, address):
        super().__init__(address)
        self.select_list[1].append(self.sock)
        self.sock.connect(self.address)

    def process_data(self, sock):
        #data should be in the form of "r:var;w:var=value;"
        #r : read/get, w : write/set
        if ";" in self.read_buffer.get(sock, ""):
            var_name, value = [i.strip() for i in self.read_buffer[sock].split("=")]
            self.state[var_name] = json.loads(value)
