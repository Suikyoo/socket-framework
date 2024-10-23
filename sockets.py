import socket

class Socket:
    #address = (ip, port)
    def __init__(self, address):
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)

        self.state = {}

        #[readers, writers]
        self.select_list = [[], [], []]
        self.read_buffer = {}
        self.write_buffer = {}

    def send(self, message, target_sock=None):
        sock = target_sock if target_sock else self.sock

        if len(self.write_buffer[sock]):
            sent = sock.send(self.write_buffer[s])
            self.write_buffer[s] = self.write_buffer[s][sent:]
 
    def recv(self, target_sock=None):
        sock = target_sock if target_sock else self.sock

        try:
            recv_string = s.recv(1024).decode()
            if recv_string == b"":
                s.shutdown(socket.SHUT_RDWR)
                s.close()

                print("socket disconnected")

            self.read_buffer[s] += recv_string

        except socket.timeout as e:
            if e.args[0] == "timed out":
                return 

    def process_data(self, sock):
        #data should be in the form of "r:var;w:var=value;"
        #r : read/get, w : write/set
        if ";" in self.read_buffer[sock]:
            cmd_token = [i.strip() for i in self.read_buffer[sock].split(";")[-1]]
            protocol, data = [i.strip() for i in cmd_token.split(":")]
            if protocol == "r":
                response_msg = f"{data}={self.state.get(data)};".encode()
                self.write_buffer[sock] += response_msg

            elif protocol == "w":
                data = [i.strip() for i in data.split("=")]
                self.state[data[0]] = data[1]

    def event_handler(self):
        readables, writables, err = select.select(*self.select_list)

        #read/recv
        for s in readables:
            if s in self.read_buffer:
                self.recv(s)

                #process commands
                self.process_data(s)

            else:
                conn, address = self.sock.accept()
                self.select_list[0].append(conn)
                self.read_buffer[conn] = ""
                self.write_buffer[conn] = ""

        #write/send
        for s in writables:
            if len(self.write_buffer[s]):
                self.send(s)




#a server's job is only to generate server-side client sockets to chat up with connecting clients on the other side
class Server(Socket):
    def __init__(self, address):
        super().__init__(address)
        self.sock.bind(self.address)
        self.sock.setblocking(False)
        self.sock.listen(5)
        
class Client(Socket):
    def __init__(self, address):
        super().__init__(address)
        self.sock.connect(self.address)
