from flask import Flask, render_template, request, redirect, session
import boto3
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# DynamoDB設定
dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-1')
)

# ダミー商品データ（DynamoDBが使えない場合用）
DUMMY_PRODUCTS = [
    {'product_id': '1', 'name': '高級腕時計', 'price': 500000, 'image': 'product1.jpg'},
    {'product_id': '2', 'name': '最新スマートフォン', 'price': 150000, 'image': 'product2.jpg'},
    {'product_id': '3', 'name': 'ゲーミングPC', 'price': 300000, 'image': 'product3.jpg'}
]

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    session['user'] = request.form['username']
    session['cart'] = []
    return redirect('/products')

@app.route('/products')
def products():
    if 'user' not in session:
        return redirect('/')
    
    # DynamoDBから商品取得を試みる
    try:
        table = dynamodb.Table('ec_unlimited_products')
        response = table.scan()
        products = response['Items']
    except:
        # エラー時はダミーデータを使用
        products = DUMMY_PRODUCTS
    
    return render_template('products.html', products=products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    product_price = int(request.form['product_price'])
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    cart.append({
        'id': product_id,
        'name': product_name,
        'price': product_price
    })
    session['cart'] = cart
    
    return redirect('/products')

@app.route('/checkout')
def checkout():
    if 'user' not in session:
        return redirect('/')
    
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    
    return render_template('checkout.html', cart=cart, total=total)

@app.route('/purchase', methods=['POST'])
def purchase():
    session['cart'] = []
    return redirect('/complete')

@app.route('/complete')
def complete():
    if 'user' not in session:
        return redirect('/')
    
    return render_template('complete.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5002)