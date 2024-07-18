import grpc
import orders_pb2
import orders_pb2_grpc

# client/orders_client.py

class OrdersServiceClient:
    def __init__(self, address='localhost:50053'):
        """Inicializa o cliente gRPC e configura o stub para comunicação com o serviço de pedidos."""

        self.channel = grpc.insecure_channel(address)
        self.stub = orders_pb2_grpc.OrdersServiceStub(self.channel)

    def create_order(self, username, books):
        """Envia uma solicitação para criar um novo pedido."""

        request = orders_pb2.CreateOrderRequest(username=username, books=books)
        return self.stub.CreateOrder(request)

    def get_order_history(self, username):
        """Envia uma solicitação para obter o histórico de pedidos de um usuário."""

        request = orders_pb2.GetOrderHistoryRequest(username=username)
        return self.stub.GetOrderHistory(request)

    def get_order_details(self, order_id):
        """Envia uma solicitação para obter os detalhes de um pedido específico pelo ID do pedido."""

        request = orders_pb2.GetOrderDetailsRequest(order_id=order_id)
        return self.stub.GetOrderDetails(request)
