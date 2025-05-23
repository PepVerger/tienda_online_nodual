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

with app.app_context():
    db.create_all()


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
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    disponibilidad = db.Column(db.Integer, nullable=False, default=20)


@app.route('/')
def index():
    categorias = Categoria.query.all()
    
    categoria_id = request.args.get('categoria_id', type=int)

    categorias = Categoria.query.all()
    if categoria_id:
        productos = Producto.query.filter_by(categoria_id=categoria_id).all()
    else:
        productos = Producto.query.all()

    return render_template('index.html', categorias=categorias, productos=productos, categoria_id=categoria_id)

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
    productos = session.get('cesta', [])
    total = sum(p['precio'] * p['cantidad'] for p in productos)
    return render_template('cesta.html', total=total, productos=productos)

@app.route('/favoritos')
def favoritos():
    return render_template('favoritos.html')

@app.route('/productos', methods=['GET'])
def productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)



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
        categoria_id = int(request.form['categoria'])
        precio_str = request.form.get('precio')

        
        if not precio_str:
            flash('El precio es obligatorio.', 'error')
            return redirect(url_for('crear_producto'))
        
        try:
            precio = float(precio_str)
        except ValueError:
            flash('El precio debe ser un número válido.', 'error')
            return redirect(url_for('crear_producto'))

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
            precio=precio,
            imagen=ruta_guardada,
            categoria_id=categoria_id
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto creado con éxito.', 'success')
        return redirect(url_for('crear_producto'))

    return render_template('crear_producto.html', categorias=categorias)


@app.route('/gestionar')
def gestionar():
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template('gestionar.html', productos=productos, categorias=categorias)


@app.route('/eliminar-producto/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('gestionar'))


@app.route('/eliminar-categoria/<int:categoria_id>', methods=['POST'])
def eliminar_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    
    if categoria.productos:  
        flash('No se puede eliminar una categoria con productos asociados.', 'danger')
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoría eliminada correctamente.', 'success')
    
    return redirect(url_for('gestionar'))


@app.route('/detalle_producto/<int:producto_id>')
def detalle_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return render_template('detalle_producto.html', producto=producto)

@app.route('/agregar-a-cesta/<int:producto_id>', methods=['POST'])
def agregar_a_cesta(producto_id):
    producto = Producto.query.get(producto_id)
    if not producto:
        flash("Producto no encontrado", "error")
        return redirect(url_for('index'))

    talla = request.form.get('talla')
    cantidad = int(request.form.get('cantidad', 1))

    cantidad_en_cesta = 0
    if 'cesta' in session:
        for i in session['cesta']:
            if i['id'] == producto_id and i['talla'] == talla:
                cantidad_en_cesta = i['cantidad']
                break

    if producto.disponibilidad < cantidad_en_cesta + cantidad:
        flash('Lo sentimos, ya no hay suficiente disponibilidad.', 'error')
        return redirect(url_for('detalle_producto', producto_id=producto.id))

    item = {
        'id': producto.id,
        'nombre': producto.nombre,
        'talla': talla,
        'precio': producto.precio,
        'imagen': producto.imagen,
        'cantidad': cantidad
    }

    if 'cesta' not in session:
        session['cesta'] = []

    cesta = session['cesta']

    for i in cesta:
        if i['id'] == producto_id and i['talla'] == talla:
            i['cantidad'] += cantidad
            break
    else:
        cesta.append(item)

    session.modified = True

    flash(f'{producto.nombre} (Talla {talla}) agregado a la cesta.', 'success')
    return redirect(url_for('cesta'))

@app.route('/actualizar_cantidad', methods=['POST'])
def actualizar_cantidad():
    index = int(request.form['id'])
    cantidad = int(request.form['cantidad'])

    cesta = session.get('cesta', [])

    if 0 <= index < len(cesta):
        if cantidad > 0:
            cesta[index]['cantidad'] = cantidad
        else:
            
            cesta.pop(index)

        session['cesta'] = cesta
        session.modified = True

    return redirect(url_for('cesta'))


@app.route('/agregar-a-favoritos/<int:producto_id>', methods=['POST'])
def agregar_a_favoritos(producto_id):
    producto = Producto.query.get_or_404(producto_id)

    item = {
        'id': producto.id,
        'nombre': producto.nombre,
        'imagen': producto.imagen,
        'precio': producto.precio
    }

    if 'favoritos' not in session:
        session['favoritos'] = []


    if not any(fav['id'] == producto.id for fav in session['favoritos']):
        session['favoritos'].append(item)
        session.modified = True
        flash(f'{producto.nombre} agregado a favoritos.', 'success')
    else:
        flash('Este producto ya está en favoritos.', 'info')

    return redirect(url_for('favoritos'))


@app.route('/eliminar-favorito/<int:producto_id>', methods=['POST'])
def eliminar_favorito(producto_id):
    favoritos = session.get('favoritos', [])
    nuevos_favoritos = [item for item in favoritos if item['id'] != producto_id]

    session['favoritos'] = nuevos_favoritos
    session.modified = True

    flash('Producto eliminado de favoritos.', 'info')
    return redirect(url_for('cesta'))
    

@app.route('/mover-a-cesta/<int:producto_id>', methods=['POST'])
def mover_a_cesta(producto_id):
    producto = Producto.query.get(producto_id)
    if not producto:
        return redirect(url_for('favoritos'))

    talla = request.form.get('talla', 'Única')
    cantidad = int(request.form.get('cantidad', 1))

    item = {
        'id': producto.id,
        'nombre': producto.nombre,
        'talla': talla,
        'precio': producto.precio,
        'imagen': producto.imagen,
        'cantidad': cantidad
    }

    if 'cesta' not in session:
        session['cesta'] = []

    for i in session['cesta']:
        if i['id'] == producto.id and i['talla'] == talla:
            i['cantidad'] += cantidad
            break
    else:
        session['cesta'].append(item)

    session.modified = True
    return redirect(url_for('cesta'))



@app.route('/comprar', methods=['POST'])
def comprar():
    session.pop('cesta', None)
    return render_template('cesta.html', mensaje="¡Gracias por su compra!")


@app.route("/ayuda")
def ayuda():
    return render_template('ayuda.html')

if __name__ == '__main__':
    if not os.path.exists('static/imgs/'):
        os.makedirs('static/imgs/')
    with app.app_context():
        db.create_all()

    app.run(debug=True)