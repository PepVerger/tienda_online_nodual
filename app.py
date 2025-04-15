from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1234'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), unique=True, nullable=False) 
    password = db.Column(db.String(256), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cuenta')
def cuenta():
    return render_template('cuenta.html')

@app.route('/login-select')
def loginselect():
    return render_template('login-select.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado', 'danger')
        else:
            new_user = User(email=email, name=name, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            

            flash('Registro exitoso.', 'success')
            
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero.', 'warning')
        return redirect(url_for('login'))

    return 'Bienvenido al panel de usuario.'


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

@app.route("/cesta")
def cesta():
    return render_template('cesta.html')

productos = [
    {
        "id": 1,
        "nombre": "Blazer cruzado estructurado",
        "descripcion": "Blazer entallado con solapa de pico y manga larga.",
        "precio": 59.95,
        "disponibilidad": True,
        "categoria": "blazers",
        "imagen": "https://static.zara.net/photos/blazer1.jpg"
    },
    {
        "id": 2,
        "nombre": "Camisa popelín básica",
        "descripcion": "Camisa clásica de algodón en popelín suave.",
        "precio": 25.95,
        "disponibilidad": True,
        "categoria": "camisas",
        "imagen": "https://static.zara.net/photos/camisa1.jpg"
    },
    {
        "id": 3,
        "nombre": "Pantalón wide leg tiro alto",
        "descripcion": "Pantalón de tiro alto y pierna ancha, estilo fluido.",
        "precio": 35.95,
        "disponibilidad": True,
        "categoria": "pantalones",
        "imagen": "https://static.zara.net/photos/pantalon1.jpg"
    },
    {
        "id": 4,
        "nombre": "Vestido midi estampado floral",
        "descripcion": "Vestido midi con estampado floral, escote en V.",
        "precio": 45.95,
        "disponibilidad": False,
        "categoria": "vestidos",
        "imagen": "https://static.zara.net/photos/vestido1.jpg"
    },
    {
        "id": 5,
        "nombre": "Cazadora efecto piel",
        "descripcion": "Chaqueta estilo biker de imitación piel.",
        "precio": 49.95,
        "disponibilidad": True,
        "categoria": "chaquetas",
        "imagen": "https://static.zara.net/photos/cazadora1.jpg"
    },
    {
        "id": 6,
        "nombre": "Falda mini denim",
        "descripcion": "Falda corta de tejido denim con bajo desflecado.",
        "precio": 29.95,
        "disponibilidad": True,
        "categoria": "faldas",
        "imagen": "https://static.zara.net/photos/falda1.jpg"
    },
    {
        "id": 7,
        "nombre": "Sudadera oversize bordado",
        "descripcion": "Sudadera de corte amplio con detalles bordados.",
        "precio": 39.95,
        "disponibilidad": True,
        "categoria": "sudaderas",
        "imagen": "https://static.zara.net/photos/sudadera1.jpg"
    },
    {
        "id": 8,
        "nombre": "Top asimétrico canalé",
        "descripcion": "Top ajustado de canalé con un solo hombro.",
        "precio": 19.95,
        "disponibilidad": True,
        "categoria": "tops",
        "imagen": "https://static.zara.net/photos/top1.jpg"
    },
    {
        "id": 9,
        "nombre": "Abrigo largo lana",
        "descripcion": "Abrigo de paño largo con cierre cruzado.",
        "precio": 89.95,
        "disponibilidad": False,
        "categoria": "abrigos",
        "imagen": "https://static.zara.net/photos/abrigo1.jpg"
    },
    {
        "id": 10,
        "nombre": "Mono largo escote halter",
        "descripcion": "Mono elegante largo con escote halter y espalda descubierta.",
        "precio": 69.95,
        "disponibilidad": True,
        "categoria": "monos",
        "imagen": "https://static.zara.net/photos/mono1.jpg"
    }
]

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)

