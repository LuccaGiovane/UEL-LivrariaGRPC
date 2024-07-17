import grpc
import catalog_pb2
import catalog_pb2_grpc

class CatalogServiceClient:
    def __init__(self, host):
        self.channel = grpc.insecure_channel(host)
        self.stub = catalog_pb2_grpc.CatalogServiceStub(self.channel)

    def get_book_info(self, title):
        request = catalog_pb2.BookRequest(title=title)
        return self.stub.GetBookInfo(request)

    def list_books(self):
        request = catalog_pb2.Empty()
        return self.stub.ListBooks(request)
