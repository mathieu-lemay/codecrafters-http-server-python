from dataclasses import dataclass
import socket
from http import HTTPStatus
from uuid import uuid4


@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, addr = server_socket.accept()

        print(f"connection from {addr[0]}:{addr[1]}")
        try:
            handle(conn)
        except Exception as e:
            print(f"Error handling connection: {e}")


def handle(conn: socket.socket) -> None:
    req_id = uuid4()
    request = parse_request(conn)
    print(f"{req_id} - Request: {request}")

    if request.path == "/":
        resp = build_empty_response(HTTPStatus.OK)
    elif request.path.startswith("/echo/"):
        resp = build_echo_response(request)
    else:
        resp = build_empty_response(HTTPStatus.NOT_FOUND)

    print(f"{req_id} - raw response:\n======\n{resp}\n======\n")
    conn.sendall(resp)
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    print(f"{req_id} - closed conn")


def parse_request(conn: socket.socket) -> Request:
    data = conn.recv(2048)
    print(f"raw request:\n======\n{data}\n======\n")

    start_line, *elements = data.split(b"\r\n")

    method, path, _ = start_line.decode().split(" ")
    headers = {}

    elem_iter = iter(elements)
    while header := next(elem_iter).decode():
        k, v = header.split(": ", maxsplit=1)
        headers[k.lower()] = v

    body = next(elem_iter, b"")

    return Request(method=method, path=path, headers=headers, body=body)


def build_empty_response(status_code: HTTPStatus) -> bytes:
    return build_response(status_code)


def build_echo_response(request: Request) -> bytes:
    body = request.path.removeprefix("/echo/").encode()
    return build_response(HTTPStatus.OK, body=body)


def build_response(
    status_code: HTTPStatus, headers: dict[str, str] | None = None, body: bytes = b""
) -> bytes:
    status = f"HTTP/1.1 {status_code} {status_code.phrase}\r\n"
    headers = {
        "Content-Type": "text/plain",
        "Content-Length": str(len(body)),
        **(headers or {}),
    }

    return (
        status.encode()
        + "\r\n".join(f"{k}: {v}" for k, v in headers.items()).encode()
        + b"\r\n\r\n"
        + body
    )


if __name__ == "__main__":
    main()
