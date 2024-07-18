import grpc
from concurrent import futures
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import catalog_pb2 as catalog_pb2
import catalog_pb2_grpc as catalog_pb2_grpc

class CatalogServiceServicer(catalog_pb2_grpc.CatalogServiceServicer):
    def __init__(self):
        """Inicializa o servidor de catálogo com uma lista de livros disponíveis."""

        self.books = [
            {"id": 1, "title": "As Aventuras na Netoland com Luccas Neto", "author": "Luccas Neto", "year": 2018, "quantity": 10, "price": 29.90},
            {"id": 2, "title": "Grandes contos", "author": "H. P. Lovecraft", "year": 2019, "quantity": 5, "price": 118.93},
            {"id": 3, "title": "Sentry: Reborn", "author": "Paul Jenkins e John Romita", "year": 2005, "quantity": 12,"price": 43.92},
            {"id": 4, "title": "A Guerra dos Tronos", "author": "George R. R. Martin", "year": 2010, "quantity": 3, "price": 54.90},
            {"id": 5, "title": "O Senhor dos Anéis", "author": "J. R. R. Tolkien", "year": 2018, "quantity": 7, "price": 89.90}
        ]

    def GetBookInfo(self, request, context):
        """Processa uma solicitação para obter informações de um livro específico pelo título."""

        for book in self.books:
            if book['title'] == request.title:
                return catalog_pb2.BookResponse(
                    id=book['id'], title=book['title'], author=book['author'], year=book['year'],
                    quantity=book['quantity'], price=book['price']
                )
        return catalog_pb2.BookResponse()

    def ListBooks(self, request, context):
        """Processa uma solicitação para listar todos os livros disponíveis no catálogo."""

        return catalog_pb2.BookList(books=[
            catalog_pb2.BookResponse(
                id=book['id'], title=book['title'], author=book['author'], year=book['year'],
                quantity=book['quantity'], price=book['price']
            ) for book in self.books
        ])

def serve():
    """Configura e inicia o servidor gRPC para o serviço de catálogo."""

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    catalog_pb2_grpc.add_CatalogServiceServicer_to_server(CatalogServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
