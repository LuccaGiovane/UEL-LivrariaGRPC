# orders_service.py
from concurrent import futures
import grpc
import orders_pb2
import orders_pb2_grpc

class OrdersService(orders_pb2_grpc.OrdersServiceServicer):
    def CreateOrder(self, request, context):
        """Processa uma solicitação para criar um novo pedido."""

        return orders_pb2.CreateOrderResponse(order_id=request.order_id)

    def GetOrderHistory(self, request, context):
        """Processa uma solicitação para obter o histórico de pedidos de um usuário."""

        return orders_pb2.GetOrderHistoryResponse()

    def GetOrderDetails(self, request, context):
        """Processa uma solicitação para obter os detalhes de um pedido específico pelo ID do pedido."""

        return orders_pb2.GetOrderDetailsResponse()

def serve():
    """Configura e inicia o servidor gRPC para o serviço de pedidos."""

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrdersServiceServicer_to_server(OrdersService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
