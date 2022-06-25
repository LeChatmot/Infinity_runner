import socket, pygame as pg, threading

class ThreadClient(threading.Thread):

    def __init__(self, conn, liste_parties):
        super().__init__(self)
        self.conn = conn
        self.liste = liste_parties

    def run(self):
        data = self.conn.recv(1024)
        data = data.decode("utf8")
        if data == "creer partie":

            #recevoir le nom de la partie
            name = self.conn.recv(1024)
            name = name.decode("utf8")

            #recevoir IP de la partie
            IP = self.conn.recv(1024)
            IP = IP.decode("utf8")

            #recevoir le port de la partie
            port = self.conn.revc(1024)
            port = port.decode("utf8")

            self.liste[name] = (IP,port)

            response = "game created"
            response = response.encode("utf8")

            socket.sendall(response)

        else:
            #verifier si la partie existe
            if data in self.liste.keys():
                response = self.liste[data]
                response = response.encode("utf8")
            
            #si nom de partie inexistant
            else:
                response = "No game named : " + data
                response = response.encode("utf8")

            socket.sendall(response)

liste_parties = {}

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', 15555))

running = True

while running:
    
    socket.listen(5)
    conn,address = socket.accept()
    print("connection client")

    my_thread = ThreadClient(conn,liste_parties)
    my_thread.start()

print("Closed")
conn.close()
socket.close()