import asyncio
from loguru import logger
from my_socket import Socket

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 KB")


class Server(Socket):
    def __init__(self):
        super(Server, self).__init__()
        self.users = []

    def set_up(self):
        self.socket.bind(("0.0.0.0", 1234))
        self.socket.listen(5)
        self.socket.setblocking(False)
        logger.debug("Server listening (debug)")

    async def send_data(self, data=None):
        for user in self.users:
            await self.main_loop.sock_sendall(user, data)

    async def listen_socket(self, listened_socket=None):
        if not listened_socket:
            return
        while True:
            try:
                data = await self.main_loop.sock_recv(listened_socket, 1024)
                await self.send_data(data)
            except ConnectionResetError:
                print("Client removed...")
                self.users.remove(listened_socket)
                return

    async def accept_sockets(self):
        while True:
            user_socket, address = await self.main_loop.sock_accept(self.socket)
            logger.debug(f"User <{address[0]}> connected!> (debug)")

            self.users.append(user_socket)
            self.main_loop.create_task(self.listen_socket(user_socket))

    async def main(self):
        await self.main_loop.create_task(self.accept_sockets())


if __name__ == '__main__':
    server = Server()
    server.set_up()

    server.start()
