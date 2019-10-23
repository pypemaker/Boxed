import concurrent.futures
import socket
from time import sleep


def accept_connection(ID):
    """Accepts a client connection and assigns player id"""
    s.listen(1)
    print(f"Waiting for Player {ID}...")

    (CLIENT, (IP, PORT)) = s.accept()
    print ("Received connection from:", IP, "source port number:", PORT, "ID:", ID)
    CLIENT.send(f'NO{ID}'.encode())

    return (ID, CLIENT)


def client_handle(source, boardcast):
    """Keep alive client handle - receive / broadcast"""
    while True:
        try:
            src_recv = source.recv(3)

            # Broadcast to every socket on the list except for the source.
            for b in boardcast:
                if b != source:
                    b.send(src_recv)

        except Exception as e:
            print(repr(e))
            return


# Create and bind TCP socket.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 9001))

# Expected number of connections.
TOTAL_CONNECTIONS = 2

# Generate a list of client IDs (starting from one).
clients = [c for c in range(1, TOTAL_CONNECTIONS + 1)]

# Empty dictionary to store the connecting clients sockets and IDs.
current_conns = {}

# Context (resource) management accepting client connections
# one a time and initiating a thread for each connection (handle).
with concurrent.futures.ThreadPoolExecutor() as executor:
    for c in clients:
        t = executor.submit(accept_connection, c)
        c_id, sock_id = t.result()
        current_conns[c_id] = sock_id

    targets = [t for t in current_conns.values()]

    for socket in targets:
        executor.submit(client_handle, socket, targets)
