import grpc
import auth_pb2
import auth_pb2_grpc

class AuthServiceClient:

    def __init__(self, address='localhost:50051'):
        self.channel = grpc.insecure_channel(address)
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def register(self, username, password):
        request = auth_pb2.RegisterRequest(username=username, password=password)
        return self.stub.Register(request)

    def login(self, username, password):
        request = auth_pb2.LoginRequest(username=username, password=password)
        return self.stub.Login(request)
