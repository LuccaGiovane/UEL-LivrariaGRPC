import grpc
import orders_pb2
import orders_pb2_grpc

# client/orders_client.py

class OrdersServiceClient:
    def __init__(self, address='localhost:50053'):
        self.channel = grpc.insecure_channel(address)
        self.stub = orders_pb2_grpc.OrdersServiceStub(self.channel)

    def create_order(self, username, books):
        request = orders_pb2.CreateOrderRequest(username=username, books=books)
        return self.stub.CreateOrder(request)

    def get_order_history(self, username):
        request = orders_pb2.GetOrderHistoryRequest(username=username)
        return self.stub.GetOrderHistory(request)

    def get_order_details(self, order_id):
        request = orders_pb2.GetOrderDetailsRequest(order_id=order_id)
        return self.stub.GetOrderDetails(request)
