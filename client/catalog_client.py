import grpc
import catalog_pb2
import catalog_pb2_grpc

class CatalogServiceClient:
    def __init__(self, host):
        """Inicializa o cliente gRPC e configura o stub para comunicação com o serviço de catálogo."""

        self.channel = grpc.insecure_channel(host)
        self.stub = catalog_pb2_grpc.CatalogServiceStub(self.channel)

    def get_book_info(self, title):
        """Envia uma solicitação para obter informações de um livro específico pelo título."""

        request = catalog_pb2.BookRequest(title=title)
        return self.stub.GetBookInfo(request)

    def list_books(self):
        """Envia uma solicitação para listar todos os livros disponíveis no catálogo."""

        request = catalog_pb2.Empty()
        return self.stub.ListBooks(request)
