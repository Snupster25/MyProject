from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)

# Модель заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    area = db.Column(db.Float, nullable=False)
    materials = db.Column(db.String(200), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

# Материалы с ценами
MATERIALS = {
    "Кирпич": 500,
    "Цемент": 300,
    "Песок": 200,
    "Щебень": 400
}

# Простая база данных пользователей
USERS = {
    "admin": "0000",
    "user": "1111"
}

# Создание таблиц в базе данных
with app.app_context():
    db.create_all()

# Главная страница (авторизация)
@app.route('/', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        if login in USERS and USERS[login] == password:
            session['user'] = login
            return redirect(url_for('dashboard'))
        else:
            error_message = 'Неверный логин или пароль'

    return render_template('login.html', error_message=error_message)

# Панель управления
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    client_name = ""
    area = ""
    selected_materials = []
    total_cost = None

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'calculate':
            client_name = request.form['client_name']
            area = float(request.form['area'])
            selected_materials = request.form.getlist('materials')
            total_cost = sum(MATERIALS[material] for material in selected_materials) * area
        elif action == 'create':
            client_name = request.form['client_name']
            area = float(request.form['area'])
            selected_materials = request.form.getlist('materials')
            total_cost = sum(MATERIALS[material] for material in selected_materials) * area
            order = Order(
                client_name=client_name,
                area=area,
                materials=', '.join(selected_materials),
                total_cost=total_cost
            )
            db.session.add(order)
            db.session.commit()
            flash('Заказ успешно создан!', 'success')
            client_name, area, selected_materials, total_cost = "", "", [], None
        elif action == 'delete' and session['user'] == 'admin':
            order_id = int(request.form['order_id'])
            order = Order.query.get(order_id)
            if order:
                db.session.delete(order)
                db.session.commit()
                flash('Заказ успешно удалён!', 'success')

    orders = Order.query.all()
    return render_template(
        'dashboard.html',
        materials=MATERIALS,
        orders=orders,
        client_name=client_name,
        area=area,
        selected_materials=selected_materials,
        total_cost=total_cost
    )

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))
