class Server(object):
    """docstring for Server."""
    def __init__(self, port):
        super(Server, self).__init__()
        self.port=port

    def start_server(self):
        print("Server started")
        
        