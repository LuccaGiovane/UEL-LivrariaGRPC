import grpc
from concurrent import futures
import auth_pb2
import auth_pb2_grpc

class AuthServiceServicer(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        self.users = {}

    def Register(self, request, context):
        if request.username in self.users:
            return auth_pb2.RegisterResponse(success=False, message="Username already exists.")
        self.users[request.username] = request.password
        return auth_pb2.RegisterResponse(success=True, message="Registration successful.")

    def Login(self, request, context):
        if request.username not in self.users or self.users[request.username] != request.password:
            return auth_pb2.LoginResponse(success=False, message="Invalid username or password.")
        return auth_pb2.LoginResponse(success=True, message="Login successful.")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)  # Corrigido aqui
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
