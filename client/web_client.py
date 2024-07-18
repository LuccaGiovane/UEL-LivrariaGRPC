import logging
import grpc
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from auth_client import AuthServiceClient
from catalog_client import CatalogServiceClient
from orders_client import OrdersServiceClient
import orders_pb2
import orders_pb2_grpc

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Instanciando os clientes gRPC com os endereços dos servidores
auth_client = AuthServiceClient('localhost:50051')
catalog_client = CatalogServiceClient('localhost:50052')
orders_client = OrdersServiceClient('localhost:50053')

@app.route('/')
def index():
    """Renderiza a página inicial e verifica se o usuário está logado."""

    logged_in = 'username' in session
    return render_template('index.html', logged_in=logged_in)

@app.route('/books')
def books():
    """Exibe a lista de livros disponíveis, obtendo-os do serviço de catálogo."""

    response = catalog_client.list_books()
    books = [{"id": book.id, "title": book.title, "author": book.author, "year": book.year, "quantity": book.quantity, "price": book.price} for book in response.books]
    logged_in = 'username' in session
    return render_template('books.html', books=books, logged_in=logged_in)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Permite que um novo usuário se registre. Se o método for POST, tenta registrar o usuário com as credenciais fornecidas."""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            response = auth_client.register(username, password)
            if response.success:
                logging.debug(f'User {username} registered successfully.')
                flash('Registration successful! Please log in.')
                return redirect(url_for('login'))
            else:
                logging.debug(f'Username {username} already exists.')
                flash('Username already exists.')
                return redirect(url_for('register'))
        except grpc.RpcError as e:
            logging.debug(f'gRPC error: {e}')
            flash('An error occurred. Please try again.')
            return redirect(url_for('register'))
    logged_in = 'username' in session
    return render_template('register.html', logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Permite que um usuário existente faça login. Se o método for POST, tenta autenticar o usuário com as credenciais fornecidas."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            response = auth_client.login(username, password)
            if response.success:
                session['username'] = username
                logging.debug(f'User {username} logged in successfully.')
                flash('Login successful!')
                return redirect(url_for('index'))
            else:
                logging.debug(f'Invalid login attempt for username: {username}')
                flash('Invalid username or password')
                return redirect(url_for('login'))
        except grpc.RpcError as e:
            logging.debug(f'gRPC error: {e}')
            flash('An error occurred. Please try again.')
            return redirect(url_for('login'))
    logged_in = 'username' in session
    return render_template('login.html', logged_in=logged_in)

@app.route('/logout')
def logout():
    """Faz logout do usuário atual e redireciona para a página inicial."""

    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Adiciona um livro ao carrinho de compras do usuário. Requer que o usuário esteja logado."""

    if 'username' not in session:
        flash('You must be logged in to add items to the cart.')
        return redirect(url_for('login'))

    book_id = int(request.form['book_id'])
    quantity = int(request.form['quantity'])

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == book_id:
            item['quantity'] += quantity
            break
    else:
        book = get_book_by_id(book_id)
        cart.append({'id': book_id, 'title': book['title'], 'author': book['author'], 'year': book['year'], 'quantity': quantity, 'price': book['price']})

    session['cart'] = cart
    return redirect(url_for('books'))

def get_book_by_id(book_id):
    """Obtém um livro pelo seu ID usando o serviço de catálogo."""

    response = catalog_client.list_books()
    for book in response.books:
        if book.id == book_id:
            return {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'year': book.year,
                'quantity': book.quantity,
                'price': book.price
            }
    return None

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    """Exibe o carrinho de compras do usuário, permitindo que ele veja e ajuste as quantidades dos itens."""

    if 'username' not in session:
        flash('You must be logged in to view your cart.')
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    for item in cart:
        book = get_book_by_id(item['id'])
        if item['quantity'] > book['quantity']:
            item['quantity'] = book['quantity']

    session['cart'] = cart
    return render_template('cart.html', cart=cart)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """Remove um item do carrinho de compras do usuário."""

    book_id = int(request.form['book_id'])

    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != book_id]

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:book_id>', methods=['POST'])
def update_cart(book_id):
    """Atualiza a quantidade de um item no carrinho de compras do usuário."""

    new_quantity = int(request.form['quantity'])
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == book_id:
            book = get_book_by_id(book_id)
            if new_quantity > book['quantity']:
                new_quantity = book['quantity']
            item['quantity'] = new_quantity
            break

    session['cart'] = cart
    return redirect(url_for('cart'))


# web_client.py

@app.route('/order', methods=['GET', 'POST'])
def order():
    """Permite que um usuário faça um pedido com os itens do seu carrinho de compras. Requer que o usuário esteja logado."""

    if 'username' not in session:
        flash('You must be logged in to place an order.')
        logging.debug('User not logged in. Redirecting to login.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        cart = session.get('cart', [])

        logging.debug(f'User {username} is attempting to place an order. Current cart: {cart}')

        if not cart:
            flash('Your cart is empty.')
            logging.debug('The cart is empty. Redirecting to books.')
            return redirect(url_for('books'))

        try:
            books = [orders_pb2.Book(title=item['title'], quantity=item['quantity']) for item in cart]
            logging.debug(f'Books to be ordered: {books}')

            response = orders_client.create_order(username, books)
            order_id = response.order_id
            logging.debug(f'Order created successfully with order_id: {order_id}')

            session.pop('cart', None)  # Clear the cart after successful order
            logging.debug('Cart cleared successfully.')

            flash(f'Order {order_id} placed successfully!')
            return redirect(url_for('orders'))  # Redirect to orders page
        except grpc.RpcError as e:
            logging.error(f'gRPC error while creating order: {e}')
            flash('An error occurred while placing the order. Please try again.')
            logging.debug('Redirecting to books due to gRPC error.')
            return redirect(url_for('books'))
    else:
        logging.debug('GET method received on /order. Redirecting to cart.')
        return redirect(url_for('cart'))


@app.route('/orders')
def orders():
    """Exibe o histórico de pedidos do usuário logado."""

    if 'username' not in session:
        flash('You must be logged in to view your orders.')
        return redirect(url_for('login'))

    username = session['username']
    try:
        response = orders_client.get_order_history(username)
        orders = []
        for order in response.orders:
            orders.append({"order_id": order.order_id, "book_titles": [book.title for book in order.books]})
        return render_template('orders.html', orders=orders)
    except grpc.RpcError as e:
        logging.debug(f'gRPC error: {e}')
        flash('An error occurred. Please try again.')
        return redirect(url_for('books'))

@app.route('/order_details/<order_id>')
def order_details(order_id):
    """Exibe os detalhes de um pedido específico. Requer que o usuário esteja logado."""

    if 'username' not in session:
        flash('You must be logged in to view order details.')
        return redirect(url_for('login'))

    try:
        response = orders_client.get_order_details(order_id)
        if response.order_id:
            order = {
                "order_id": response.order_id,
                "username": response.username,
                "books": [{"title": book.title, "quantity": book.quantity} for book in response.books],
                "date": response.date
            }
            return render_template('order_details.html', order=order)
        else:
            flash('Order not found.')
            return redirect(url_for('orders'))
    except grpc.RpcError as e:
        logging.debug(f'gRPC error: {e}')
        flash('An error occurred. Please try again.')
        return redirect(url_for('orders'))

@app.route('/users')
def users():
    """Exibe uma lista de todos os usuários registrados."""

    try:
        response = auth_client.get_users()
        users = [{"username": user.username} for user in response.users]
        return render_template('users.html', users=users)
    except grpc.RpcError as e:
        logging.debug(f'gRPC error: {e}')
        flash('An error occurred. Please try again.')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
