import grpc
from concurrent import futures
import orders_pb2
import orders_pb2_grpc
import uuid
from datetime import datetime

class OrdersServiceServicer(orders_pb2_grpc.OrdersServiceServicer):
    def __init__(self):
        self.orders = {}

    def CreateOrder(self, request, context):
        order_id = str(uuid.uuid4())
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.orders[order_id] = {
            "order_id": order_id,
            "username": request.username,
            "books": [{"title": book.title, "quantity": book.quantity} for book in request.books],
            "date": date
        }
        return orders_pb2.CreateOrderResponse(order_id=order_id)

    def GetOrderHistory(self, request, context):
        user_orders = [orders_pb2.Order(
            order_id=order["order_id"],
            username=order["username"],
            books=[orders_pb2.Book(title=book["title"], quantity=book["quantity"]) for book in order["books"]],
            date=order["date"]
        ) for order in self.orders.values() if order["username"] == request.username]
        return orders_pb2.GetOrderHistoryResponse(orders=user_orders)

    def GetOrderDetails(self, request, context):
        order = self.orders.get(request.order_id)
        if order:
            return orders_pb2.GetOrderDetailsResponse(
                order_id=order["order_id"],
                username=order["username"],
                books=[orders_pb2.Book(title=book["title"], quantity=book["quantity"]) for book in order["books"]],
                date=order["date"]
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Order not found')
        return orders_pb2.GetOrderDetailsResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrdersServiceServicer_to_server(OrdersServiceServicer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
