import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, addr = server_socket.accept()

        print(f"connection from {addr[0]}:{addr[1]}")
        with conn:
            handle(conn)
            conn.shutdown(socket.SHUT_RDWR)


def handle(conn: socket.socket) -> None:
    conn.send(b"HTTP/1.1 200 OK\r\n\r\n")


if __name__ == "__main__":
    main()
