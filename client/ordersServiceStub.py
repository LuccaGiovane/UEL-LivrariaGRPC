import grpc
import orders_pb2 as orders__pb2

class OrdersServiceStub(object):
    def __init__(self, channel):
        self.CreateOrder = channel.unary_unary(
            '/orders.OrdersService/CreateOrder',
            request_serializer=orders__pb2.CreateOrderRequest.SerializeToString,
            response_deserializer=orders__pb2.CreateOrderResponse.FromString,
        )
