from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1234'
app.config['UPLOAD_FOLDER'] = 'static/imgs/'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(200))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)


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


@app.route('/crear-categoria', methods=['GET', 'POST'])
def crear_categoria():
    if request.method == 'POST':
        nombre = request.form['nombre']
        if Categoria.query.filter_by(nombre=nombre).first():
            flash('La categoría ya existe.', 'warning')
        else:
            nueva_categoria = Categoria(nombre=nombre)
            db.session.add(nueva_categoria)
            db.session.commit()
            flash('Categoría creada con éxito.', 'success')
            return redirect(url_for('crear_categoria'))
    return render_template('crear_categoria.html')


@app.route('/crear-producto', methods=['GET', 'POST'])
def crear_producto():
    categorias = Categoria.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        categoria_id = request.form['categoria']
        imagen = request.files['imagen']

        if imagen:
            filename = secure_filename(imagen.filename)
            ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(ruta_imagen)
            ruta_guardada = f'{app.config["UPLOAD_FOLDER"]}{filename}'
        else:
            ruta_guardada = None

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            imagen=ruta_guardada,
            categoria_id=categoria_id
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto creado con éxito.', 'success')
        return redirect(url_for('crear_producto'))

    return render_template('crear_producto.html', categorias=categorias)


if __name__ == '__main__':
    if not os.path.exists('static/imgs/'):
        os.makedirs('static/imgs/')
    with app.app_context():
        db.create_all()
    app.run(debug=True)
