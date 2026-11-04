from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import func
from datetime import datetime
from functools import wraps
import traceback
import json
import math

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/db_celulares_jireh'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_secreta_experto_mvc'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ==========================================
# 0. DECORADORES DE SEGURIDAD Y ROLES
# ==========================================
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('estadologin'):
            if request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'msg': 'Su sesión ha expirado. Inicie sesión nuevamente.'})
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('estadologin'):
            if request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'msg': 'Su sesión ha expirado. Inicie sesión nuevamente.'})
            return redirect(url_for('login'))
        if session.get('rol') != 'ADMINISTRADOR':
            if request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'msg': 'Acceso denegado: Se requieren permisos de Administrador.'})
            flash('Acceso Restringido: No tienes permisos de Administrador para ingresar a la sección solicitada.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 1. ORM: SEGURIDAD Y ROLES
# ==========================================
class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    personal = db.relationship('Personal', backref='rol_asignado', lazy=True)

class Personal(db.Model):
    __tablename__ = 'personal'
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)
    
    ordenes_atendidas = db.relationship('OrdenServicio', backref='tecnico', lazy=True)
    ventas_realizadas = db.relationship('Venta', backref='cajero', lazy=True)

# ==========================================
# 2. ORM: INVENTARIO Y CATÁLOGO CONTROLADO
# ==========================================
class CategoriaCatalogo(db.Model):
    __tablename__ = 'categoria_catalogo'
    id = db.Column(db.Integer, primary_key=True)
    seccion = db.Column(db.String(50), nullable=False) # TIPO_ACCESORIO, CALIDAD_REPUESTO, MARCA_REPUESTO
    nombre = db.Column(db.String(100), nullable=False)

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(150), nullable=False)
    ruc = db.Column(db.String(11), unique=True, nullable=True) 
    telefono = db.Column(db.String(15))
    repuestos_provistos = db.relationship('Repuesto', backref='proveedor_oficial', lazy=True)

class Repuesto(db.Model):
    __tablename__ = 'repuesto'
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    modelos_compatibles = db.Column(db.String(255), nullable=True)
    calidad = db.Column(db.String(50), nullable=False) 
    costo = db.Column(db.Numeric(10, 2), nullable=False)
    precio_cliente = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=1)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=True)

class Accesorio(db.Model):
    __tablename__ = 'accesorio'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=True)
    modelo = db.Column(db.String(100), nullable=True)
    modelos_compatibles = db.Column(db.String(255), nullable=True)
    caracteristicas = db.Column(db.String(255), nullable=True)
    costo = db.Column(db.Numeric(10, 2), nullable=False)
    precio_cliente = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=1)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=True)

class Celular(db.Model):
    __tablename__ = 'celular'
    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(15), unique=True, nullable=False) 
    imei2 = db.Column(db.String(15), nullable=True) 
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    codigo_modelo = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(50), nullable=False)
    ram = db.Column(db.String(20), nullable=False)
    rom = db.Column(db.String(20), nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)
    precio_cliente = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(50), default='NUEVO')
    disponible = db.Column(db.Boolean, default=True) 
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'), nullable=True)

# ==========================================
# 3. ORM: VENTAS Y SERVICIO TÉCNICO
# ==========================================
class Venta(db.Model):
    __tablename__ = 'venta'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_comprobante = db.Column(db.String(20), nullable=False) 
    documento_cliente = db.Column(db.String(15), nullable=False) 
    nombre_cliente = db.Column(db.String(150), nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False) 
    total = db.Column(db.Numeric(10, 2), nullable=False)
    personal_id = db.Column(db.Integer, db.ForeignKey('personal.id'), nullable=False)
    detalles = db.relationship('DetalleVenta', backref='venta_asociada', lazy=True)

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    tipo_producto = db.Column(db.String(50), nullable=False) 
    producto_id = db.Column(db.Integer, nullable=False) 
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'
    id = db.Column(db.Integer, primary_key=True)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    documento_cliente = db.Column(db.String(15), nullable=False)
    nombre_cliente = db.Column(db.String(150), nullable=False)
    telefono_cliente = db.Column(db.String(15), nullable=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    imei_serie = db.Column(db.String(50), nullable=True)
    patron_contrasena = db.Column(db.String(50), nullable=True)
    falla_reportada = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(50), default='RECEPCIONADO') 
    costo_mano_obra = db.Column(db.Numeric(10, 2), default=0.00)
    total = db.Column(db.Numeric(10, 2), default=0.00)
    acuenta = db.Column(db.Numeric(10, 2), default=0.00)
    saldo = db.Column(db.Numeric(10, 2), default=0.00)
    
    personal_id = db.Column(db.Integer, db.ForeignKey('personal.id'), nullable=False)
    repuestos_usados = db.relationship('DetalleOrdenRepuesto', backref='orden_asociada', lazy=True)

class DetalleOrdenRepuesto(db.Model):
    __tablename__ = 'detalle_orden_repuesto'
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=False)
    repuesto_id = db.Column(db.Integer, nullable=False) 
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

# Semilla automática de opciones autorizadas
def inicializar_catalogo():
    opciones_base = {
        'TIPO_ACCESORIO': ["FUNDA CASE", "MICA DE VIDRIO", "MICA HIDROGEL", "CABLE USB", "CARGADOR", "AURICULARES"],
        'CALIDAD_REPUESTO': ["ORIGINAL", "AMOLED BORDE FINO", "OLED", "INCELL / GENÉRICA", "BATERÍA ORIGINAL", "ZÓCALO / FLEX CARGA"],
        'MARCA_REPUESTO': ["XIAOMI", "SAMSUNG", "HONOR", "MOTOROLA", "APPLE", "REALME", "ZTE", "INFINIX"]
    }
    for seccion, lista in opciones_base.items():
        existentes = CategoriaCatalogo.query.filter_by(seccion=seccion).count()
        if existentes == 0:
            for item in lista:
                db.session.add(CategoriaCatalogo(seccion=seccion, nombre=item))
    db.session.commit()

# API exclusiva para que el Administrador agregue nuevas opciones
@app.route('/api/agregar_opcion_catalogo', methods=['POST'])
@admin_requerido
def agregar_opcion_catalogo():
    try:
        datos = request.json
        seccion = datos.get('seccion', '').strip().upper()
        nombre = datos.get('nombre', '').strip().upper()
        
        if not seccion or not nombre:
            return jsonify({'status': 'error', 'msg': 'Debe escribir un nombre válido.'})
            
        existe = CategoriaCatalogo.query.filter_by(seccion=seccion, nombre=nombre).first()
        if existe:
            return jsonify({'status': 'error', 'msg': f'La opción "{nombre}" ya existe en la lista.'})
            
        nueva_op = CategoriaCatalogo(seccion=seccion, nombre=nombre)
        db.session.add(nueva_op)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': f'Opción "{nombre}" añadida correctamente.', 'nombre': nombre})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'msg': str(e)})

# ==========================================
# 4. CONTROLADORES PRINCIPALES Y LOGIN
# ==========================================
@app.route('/')
@login_requerido
def index():
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    
    ventas_mes = Venta.query.filter(
        db.extract('month', Venta.fecha_hora) == mes_actual,
        db.extract('year', Venta.fecha_hora) == anio_actual
    ).all()
    total_ventas = sum(float(v.total) for v in ventas_mes)
    
    servicios_mes = OrdenServicio.query.filter(
        db.extract('month', OrdenServicio.fecha_ingreso) == mes_actual,
        db.extract('year', OrdenServicio.fecha_ingreso) == anio_actual,
        OrdenServicio.estado == 'ENTREGADO'
    ).all()
    total_servicios = sum(float(s.total) for s in servicios_mes)
    
    total_general = total_ventas + total_servicios
    
    equipos_pendientes = OrdenServicio.query.filter(
        OrdenServicio.estado.in_(['RECEPCIONADO', 'EN REPARACIÓN', 'LISTO'])
    ).order_by(OrdenServicio.fecha_ingreso.desc()).limit(5).all()
    
    stock_accesorios = Accesorio.query.filter(Accesorio.stock < 3).limit(5).all()
    stock_repuestos = Repuesto.query.filter(Repuesto.stock < 3).limit(5).all()
    
    alertas_stock = []
    for a in stock_accesorios:
        alertas_stock.append({'tipo': 'ACCESORIO', 'nombre': f"{a.tipo} {a.marca if a.marca else ''} {a.modelo if a.modelo else ''}".strip(), 'stock': a.stock})
    for r in stock_repuestos:
        alertas_stock.append({'tipo': 'REPUESTO', 'nombre': f"{r.marca} {r.modelo}", 'stock': r.stock})

    return render_template(
        'index.html', 
        total_ventas=total_ventas, 
        total_servicios=total_servicios, 
        total_general=total_general,
        equipos_pendientes=equipos_pendientes,
        alertas_stock=alertas_stock
    )

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/validar_login', methods=['POST'])
def validar_login():
    try:
        usuario = request.form.get('usuario')
        password = request.form.get('password')

        if not usuario or not password:
            return jsonify({'status': 'error', 'msg': 'Ingrese credenciales.'})

        user = Personal.query.filter_by(usuario=usuario).first()

        if user and bcrypt.check_password_hash(user.password_hash, password): 
            session['estadologin'] = True
            session['id_personal'] = user.id
            session['alias'] = user.nombres.split(' ')[0] 
            session['rol'] = user.rol_asignado.nombre
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'msg': 'Credenciales incorrectas.'})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error interno: {str(e)}'})

# ==========================================
# 5. RUTAS DE PERFIL DE USUARIO
# ==========================================
@app.route('/perfil')
@login_requerido
def perfil():
    user = Personal.query.get(session['id_personal'])
    return render_template('perfil.html', user=user)

@app.route('/api/actualizar_perfil', methods=['POST'])
@login_requerido
def actualizar_perfil():
    try:
        user = Personal.query.get(session['id_personal'])
        usuario_nuevo = request.form.get('usuario')
        pwd_actual = request.form.get('password_actual')
        pwd_nueva = request.form.get('password_nueva')
        pwd_confirma = request.form.get('password_confirmar')
        
        if not pwd_actual:
            return jsonify({'status': 'error', 'msg': 'Debe ingresar su contraseña actual.'})
            
        if not bcrypt.check_password_hash(user.password_hash, pwd_actual):
            return jsonify({'status': 'error', 'msg': 'La contraseña actual es incorrecta.'})
            
        if usuario_nuevo != user.usuario:
            if Personal.query.filter_by(usuario=usuario_nuevo).first():
                return jsonify({'status': 'error', 'msg': 'El nombre de usuario ya está en uso.'})
            user.usuario = usuario_nuevo
            
        if pwd_nueva:
            if pwd_nueva != pwd_confirma:
                return jsonify({'status': 'error', 'msg': 'Las contraseñas nuevas no coinciden.'})
            user.password_hash = bcrypt.generate_password_hash(pwd_nueva).decode('utf-8')
            
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Perfil actualizado correctamente.'})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error interno: {str(e)}'})

# ==========================================
# 6. MÓDULO DE PERSONAL (SOLO ADMINISTRADOR)
# ==========================================
@app.route('/personal')
@admin_requerido
def personal():
    roles = Rol.query.all()
    return render_template('personal.html', roles=roles)

@app.route('/api/crear_personal', methods=['POST'])
@admin_requerido
def crear_personal():
    try:
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        usuario = request.form.get('usuario')
        rol_id = request.form.get('rol_id')

        if Personal.query.filter_by(usuario=usuario).first():
            return jsonify({'status': 'error', 'msg': 'El nombre de usuario ya está registrado.'})

        hashed_password = bcrypt.generate_password_hash('123456').decode('utf-8')
        
        nuevo_personal = Personal(nombres=nombres, apellidos=apellidos, usuario=usuario, password_hash=hashed_password, rol_id=rol_id)
        db.session.add(nuevo_personal)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Personal creado. Contraseña por defecto: 123456'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error: {str(e)}'})

# ==========================================
# 7. RUTAS DE INVENTARIO: REPUESTOS
# ==========================================
@app.route('/repuestos')
@login_requerido
def repuestos():
    lista_repuestos = Repuesto.query.all()
    return render_template('repuestos.html', repuestos=lista_repuestos)

@app.route('/nuevo_repuesto')
@login_requerido
def nuevo_repuesto():
    marca_modelos = {}
    memoria_compatibles = {} 
    
    repuestos_db = Repuesto.query.all()
    for r in repuestos_db:
        marca = r.marca.strip().upper()
        modelo = r.modelo.strip().upper()
        
        if marca not in marca_modelos: marca_modelos[marca] = set()
        marca_modelos[marca].add(modelo)
        
        if r.modelos_compatibles:
            if modelo not in memoria_compatibles: memoria_compatibles[modelo] = set()
            for mc in r.modelos_compatibles.split(','):
                if mc.strip():
                    marca_modelos[marca].add(mc.strip().upper())
                    memoria_compatibles[modelo].add(mc.strip().upper())

    for m in marca_modelos: marca_modelos[m] = sorted(list(marca_modelos[m]))
    for mod in memoria_compatibles: memoria_compatibles[mod] = ", ".join(sorted(list(memoria_compatibles[mod])))
        
    marcas_autorizadas = [c.nombre for c in CategoriaCatalogo.query.filter_by(seccion='MARCA_REPUESTO').order_by(CategoriaCatalogo.nombre).all()]
    calidades_autorizadas = [c.nombre for c in CategoriaCatalogo.query.filter_by(seccion='CALIDAD_REPUESTO').order_by(CategoriaCatalogo.nombre).all()]
    proveedores = Proveedor.query.all()
    
    return render_template('form_repuesto.html', 
                           marcas_autorizadas=marcas_autorizadas,
                           calidades_autorizadas=calidades_autorizadas,
                           marca_modelos=marca_modelos, 
                           memoria_compatibles=memoria_compatibles, 
                           proveedores=proveedores)

@app.route('/api/guardar_repuesto', methods=['POST'])
@login_requerido
def guardar_repuesto():
    try:
        marca = (request.form.get('marca') or '').strip().upper()
        calidad = (request.form.get('calidad') or '').strip().upper()
        modelo = (request.form.get('modelo') or '').strip().upper()
        modelos_compatibles = (request.form.get('modelos_compatibles') or '').strip().upper() # OPCIONAL
        costo_raw = request.form.get('costo')
        stock_raw = request.form.get('stock')
        proveedor_input = (request.form.get('proveedor_id') or '').strip().upper()
        
        # 1. Validación estricta de campos obligatorios
        if not marca or not calidad or not modelo or not costo_raw or not stock_raw or not proveedor_input:
            return jsonify({'status': 'error', 'msg': 'Todos los campos (Marca, Calidad, Modelo, Costo, Stock y Proveedor) son obligatorios.'})

        if len(proveedor_input) < 2 or proveedor_input.isdigit():
            return jsonify({'status': 'error', 'msg': 'Ingrese un nombre de Proveedor válido (no números sueltos ni en blanco).'})

        costo = float(costo_raw)
        stock = int(stock_raw)
        if costo <= 0 or stock < 1:
            return jsonify({'status': 'error', 'msg': 'El costo y el stock deben ser mayores a cero.'})

        if not CategoriaCatalogo.query.filter_by(seccion='MARCA_REPUESTO', nombre=marca).first():
            return jsonify({'status': 'error', 'msg': 'Seleccione una Marca autorizada.'})
        if not CategoriaCatalogo.query.filter_by(seccion='CALIDAD_REPUESTO', nombre=calidad).first():
            return jsonify({'status': 'error', 'msg': 'Seleccione un Componente/Calidad autorizado.'})

        # 2. Cálculo interno: Redondeo a múltiplo de 5 + S/ 50.00
        costo_redondeado = math.ceil(costo / 5.0) * 5.0
        precio_cliente = costo_redondeado + 50.0

        # 3. Buscar o crear Proveedor por su nombre real
        prov_db = Proveedor.query.filter_by(razon_social=proveedor_input).first()
        if prov_db:
            proveedor_final_id = prov_db.id
        else:
            nuevo_prov = Proveedor(razon_social=proveedor_input)
            db.session.add(nuevo_prov)
            db.session.flush()
            proveedor_final_id = nuevo_prov.id

        modelos_entrantes = {modelo}
        if modelos_compatibles:
            for mc in modelos_compatibles.split(','):
                if mc.strip(): modelos_entrantes.add(mc.strip().upper())

        candidatos = Repuesto.query.filter_by(marca=marca, calidad=calidad).all()
        repuesto_existente = None
        
        for cand in candidatos:
            modelos_cand = {cand.modelo.strip().upper()}
            if cand.modelos_compatibles:
                for mc in cand.modelos_compatibles.split(','):
                    if mc.strip(): modelos_cand.add(mc.strip().upper())
            
            if modelos_entrantes.intersection(modelos_cand):
                repuesto_existente = cand
                modelos_cand.update(modelos_entrantes)
                modelos_cand.discard(cand.modelo.strip().upper())
                cand.modelos_compatibles = ", ".join(sorted(list(modelos_cand))) if modelos_cand else None
                cand.stock += stock
                cand.costo = costo
                cand.precio_cliente = precio_cliente
                cand.proveedor_id = proveedor_final_id
                break

        if repuesto_existente:
            msg = f'Coincidencia encontrada: Stock sumado y precio actualizado a S/ {precio_cliente:.2f}.'
        else:
            modelos_entrantes.discard(modelo) 
            str_compatibles = ", ".join(sorted(list(modelos_entrantes))) if modelos_entrantes else None
            nuevo_rep = Repuesto(
                marca=marca, modelo=modelo, modelos_compatibles=str_compatibles,
                calidad=calidad, costo=costo, precio_cliente=precio_cliente,
                stock=stock, proveedor_id=proveedor_final_id
            )
            db.session.add(nuevo_rep)
            msg = f'Nuevo repuesto registrado con precio público S/ {precio_cliente:.2f}.'
            
        db.session.commit()
        return jsonify({'status': 'success', 'msg': msg})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error: {str(e)}'})
# ==========================================
# 8. RUTAS DE INVENTARIO: ACCESORIOS
# ==========================================
@app.route('/accesorios')
@login_requerido
def accesorios():
    lista_accesorios = Accesorio.query.all()
    proveedores = Proveedor.query.all() 
    tipos_unicos = [c.nombre for c in CategoriaCatalogo.query.filter_by(seccion='TIPO_ACCESORIO').order_by(CategoriaCatalogo.nombre).all()]
    marcas_unicas = sorted(list(set([a.marca.strip().upper() for a in lista_accesorios if a.marca and a.marca != "GENÉRICA"])))
    return render_template('accesorios.html', accesorios=lista_accesorios, proveedores=proveedores, tipos=tipos_unicos, marcas=marcas_unicas)

@app.route('/api/recargar_accesorio', methods=['POST'])
@login_requerido
def recargar_accesorio():
    try:
        id_acc = request.form.get('id_accesorio')
        costo_nuevo = request.form.get('costo_recarga')
        precio_nuevo = request.form.get('precio_cliente_recarga')
        stock_agregar = int(request.form.get('stock_recarga'))
        proveedor_input = request.form.get('proveedor_id_recarga')
        
        acc = Accesorio.query.get(id_acc)
        if not acc: return jsonify({'status': 'error', 'msg': 'Accesorio no encontrado.'})

        proveedor_final_id = None
        if proveedor_input:
            if proveedor_input.isdigit(): proveedor_final_id = int(proveedor_input)
            else:
                nuevo_prov = Proveedor(razon_social=proveedor_input.strip().upper())
                db.session.add(nuevo_prov)
                db.session.flush()
                proveedor_final_id = nuevo_prov.id

        acc.stock += stock_agregar
        acc.costo = costo_nuevo
        acc.precio_cliente = precio_nuevo
        acc.proveedor_id = proveedor_final_id
        db.session.commit()
        return jsonify({'status': 'success', 'msg': f'Stock sumado. Total: {acc.stock} und.'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})

@app.route('/nuevo_accesorio')
@login_requerido
def nuevo_accesorio():
    # Solo mostramos los tipos autorizados en CategoriaCatalogo
    tipos_limpios = [c.nombre for c in CategoriaCatalogo.query.filter_by(seccion='TIPO_ACCESORIO').order_by(CategoriaCatalogo.nombre).all()]
    
    marca_modelos = {}
    memoria_compatibles = {}
    memoria_specs = {} 
    
    accesorios_db = Accesorio.query.all()
    for a in accesorios_db:
        tipo = a.tipo.strip().upper()
        marca = a.marca.strip().upper() if a.marca else "GENÉRICA"
        modelo = a.modelo.strip().upper() if a.modelo else ""
        
        if marca not in marca_modelos: marca_modelos[marca] = set()
        if modelo: marca_modelos[marca].add(modelo)
        
        if a.modelos_compatibles:
            if modelo not in memoria_compatibles: memoria_compatibles[modelo] = set()
            for mc in a.modelos_compatibles.split(','):
                if mc.strip():
                    marca_modelos[marca].add(mc.strip().upper())
                    memoria_compatibles[modelo].add(mc.strip().upper())
                    
        if a.caracteristicas:
            if tipo not in memoria_specs: memoria_specs[tipo] = {}
            if marca not in memoria_specs[tipo]: memoria_specs[tipo][marca] = set()
            memoria_specs[tipo][marca].add(a.caracteristicas.strip().upper())

    for m in marca_modelos: marca_modelos[m] = sorted(list(marca_modelos[m]))
    for mod in memoria_compatibles: memoria_compatibles[mod] = ", ".join(sorted(list(memoria_compatibles[mod])))
    for t in memoria_specs:
        for m in memoria_specs[t]:
            memoria_specs[t][m] = sorted(list(memoria_specs[t][m]))
            
    proveedores = Proveedor.query.all()
    return render_template('form_accesorio.html', tipos=tipos_limpios, marca_modelos=marca_modelos, memoria_compatibles=memoria_compatibles, memoria_specs=memoria_specs, proveedores=proveedores)

@app.route('/api/guardar_accesorio', methods=['POST'])
@login_requerido
def guardar_accesorio():
    try:
        tipo = (request.form.get('tipo') or '').strip().upper()
        marca = (request.form.get('marca') or '').strip().upper()
        modelo = (request.form.get('modelo') or '').strip().upper()
        modelos_compatibles = (request.form.get('modelos_compatibles') or '').strip().upper() # OPCIONAL
        caracteristicas = (request.form.get('caracteristicas') or '').strip().upper()
        costo_raw = request.form.get('costo')
        stock_raw = request.form.get('stock')
        proveedor_input = (request.form.get('proveedor_id') or '').strip().upper()
        
        # 1. Validación estricta: Tipo, Marca, Modelo, Costo, Stock y Proveedor son SÍ O SÍ obligatorios
        if not tipo or not marca or not modelo or not costo_raw or not stock_raw or not proveedor_input:
            return jsonify({'status': 'error', 'msg': 'Todos los campos principales (Tipo, Marca, Modelo, Costo, Stock y Proveedor) son obligatorios.'})

        if len(proveedor_input) < 2 or proveedor_input.isdigit():
            return jsonify({'status': 'error', 'msg': 'Ingrese un nombre de Proveedor válido (no números sueltos ni en blanco).'})

        es_funda_o_mica = any(p in tipo for p in ['MICA', 'FUNDA', 'CASE', 'PROTECTOR'])
        if not es_funda_o_mica and not caracteristicas:
            return jsonify({'status': 'error', 'msg': 'Debe ingresar las Especificaciones / Características del accesorio.'})

        costo = float(costo_raw)
        stock = int(stock_raw)
        if costo <= 0 or stock < 1:
            return jsonify({'status': 'error', 'msg': 'El costo y el stock deben ser mayores a cero.'})

        if not CategoriaCatalogo.query.filter_by(seccion='TIPO_ACCESORIO', nombre=tipo).first():
            return jsonify({'status': 'error', 'msg': 'Tipo de accesorio no autorizado.'})

        # 2. Cálculo interno: Suma interna (x2) redondeado al múltiplo de 5 superior
        precio_cliente = math.ceil((costo * 2.0) / 5.0) * 5.0
        
        # 3. Buscar o crear Proveedor por su nombre real
        prov_db = Proveedor.query.filter_by(razon_social=proveedor_input).first()
        if prov_db:
            proveedor_final_id = prov_db.id
        else:
            nuevo_prov = Proveedor(razon_social=proveedor_input)
            db.session.add(nuevo_prov)
            db.session.flush()
            proveedor_final_id = nuevo_prov.id

        modelos_entrantes = {modelo}
        if modelos_compatibles:
            for mc in modelos_compatibles.split(','):
                if mc.strip(): modelos_entrantes.add(mc.strip().upper())

        candidatos = Accesorio.query.filter_by(tipo=tipo, marca=marca).all()
        accesorio_existente = None
        
        for cand in candidatos:
            modelos_cand = {cand.modelo.strip().upper()} if cand.modelo else set()
            if cand.modelos_compatibles:
                for mc in cand.modelos_compatibles.split(','):
                    if mc.strip(): modelos_cand.add(mc.strip().upper())
            
            if es_funda_o_mica:
                if modelos_entrantes.intersection(modelos_cand):
                    accesorio_existente = cand
                    modelos_cand.update(modelos_entrantes)
                    if cand.modelo and cand.modelo.strip().upper() in modelos_cand:
                        modelos_cand.discard(cand.modelo.strip().upper())
                    cand.modelos_compatibles = ", ".join(sorted(list(modelos_cand))) if modelos_cand else None
                    cand.stock += stock
                    cand.costo = costo
                    cand.precio_cliente = precio_cliente
                    cand.proveedor_id = proveedor_final_id
                    break 
            else:
                if (cand.modelo or '').strip().upper() == modelo and (cand.caracteristicas or '').strip().upper() == caracteristicas:
                    accesorio_existente = cand
                    cand.stock += stock
                    cand.costo = costo
                    cand.precio_cliente = precio_cliente
                    cand.proveedor_id = proveedor_final_id
                    break

        if accesorio_existente:
            msg = f'Coincidencia encontrada: Stock sumado y precio fijado en S/ {precio_cliente:.2f}.'
        else:
            modelos_entrantes.discard(modelo)
            str_compatibles = ", ".join(sorted(list(modelos_entrantes))) if modelos_entrantes else None
            nuevo_acc = Accesorio(
                tipo=tipo, marca=marca, modelo=modelo,
                modelos_compatibles=str_compatibles, caracteristicas=caracteristicas if caracteristicas else None,
                costo=costo, precio_cliente=precio_cliente, stock=stock, proveedor_id=proveedor_final_id
            )
            db.session.add(nuevo_acc)
            msg = f'Nuevo accesorio registrado con precio al cliente S/ {precio_cliente:.2f}.'
            
        db.session.commit()
        return jsonify({'status': 'success', 'msg': msg})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error interno: {str(e)}'})

# ==========================================
# 9. RUTAS DE INVENTARIO: CELULARES
# ==========================================
@app.route('/celulares')
@login_requerido
def celulares():
    lista_celulares = Celular.query.filter_by(disponible=True).all()
    return render_template('celulares.html', celulares=lista_celulares)

@app.route('/nuevo_celular')
@login_requerido
def nuevo_celular():
    marca_modelos = {}
    celulares_db = Celular.query.all()
    for c in celulares_db:
        marca = c.marca.strip().upper()
        modelo = c.modelo.strip().upper()
        if marca not in marca_modelos: marca_modelos[marca] = set()
        marca_modelos[marca].add(modelo)
        
    for m in marca_modelos: marca_modelos[m] = sorted(list(marca_modelos[m]))
    proveedores = Proveedor.query.all()
    return render_template('form_celular.html', marca_modelos=marca_modelos, proveedores=proveedores)

@app.route('/api/guardar_celular', methods=['POST'])
@login_requerido
def guardar_celular():
    try:
        imei = request.form.get('imei').strip()
        imei2 = request.form.get('imei2').strip() if request.form.get('imei2') else None

        if len(imei) != 15 or not imei.isdigit():
            return jsonify({'status': 'error', 'msg': 'El IMEI 1 debe tener exactamente 15 dígitos.'})
        
        if imei2:
            if len(imei2) != 15 or not imei2.isdigit():
                return jsonify({'status': 'error', 'msg': 'El IMEI 2 debe tener exactamente 15 dígitos.'})
            if imei == imei2:
                return jsonify({'status': 'error', 'msg': 'El IMEI 1 y el IMEI 2 no pueden ser idénticos.'})

        if Celular.query.filter((Celular.imei == imei) | (Celular.imei2 == imei)).first():
            return jsonify({'status': 'error', 'msg': f'El IMEI Principal {imei} ya existe en otro equipo.'})
            
        if imei2 and Celular.query.filter((Celular.imei == imei2) | (Celular.imei2 == imei2)).first():
            return jsonify({'status': 'error', 'msg': f'El IMEI Secundario {imei2} ya existe en otro equipo.'})

        marca = request.form.get('marca').strip().upper()
        modelo = request.form.get('modelo').strip().upper()
        codigo_modelo = request.form.get('codigo_modelo').strip().upper()
        color = request.form.get('color').strip().upper()
        ram = request.form.get('ram')
        rom = request.form.get('rom')
        costo = request.form.get('costo')
        precio_cliente = request.form.get('precio_cliente')
        
        proveedor_input = request.form.get('proveedor_id')
        proveedor_final_id = None
        if proveedor_input:
            if proveedor_input.isdigit(): proveedor_final_id = int(proveedor_input)
            else:
                nuevo_prov = Proveedor(razon_social=proveedor_input.strip().upper())
                db.session.add(nuevo_prov)
                db.session.flush()
                proveedor_final_id = nuevo_prov.id

        nuevo_celular = Celular(imei=imei, imei2=imei2, marca=marca, modelo=modelo, codigo_modelo=codigo_modelo, color=color, ram=ram, rom=rom, costo=costo, precio_cliente=precio_cliente, proveedor_id=proveedor_final_id)
        db.session.add(nuevo_celular)
        db.session.commit()
        return jsonify({'status': 'success', 'msg': f'Equipo {marca} {modelo} registrado con éxito.'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error interno: {str(e)}'})

# ==========================================
# 10. RUTAS: PUNTO DE VENTA (POS)
# ==========================================
@app.route('/punto_venta')
@login_requerido
def punto_venta():
    return render_template('punto_venta.html')

@app.route('/api/buscar_productos')
@login_requerido
def api_buscar_productos():
    q = request.args.get('q', '').strip().upper()
    if not q: return jsonify([])
    
    resultados = []
    
    celulares = Celular.query.filter(Celular.disponible == True, 
        (Celular.imei.contains(q)) | (Celular.imei2.contains(q)) | (Celular.marca.contains(q)) | (Celular.modelo.contains(q))
    ).limit(10).all()
    for c in celulares:
        resultados.append({'id': f"CEL-{c.id}", 'tipo': 'CELULAR', 'descripcion': f"📱 {c.marca} {c.modelo} ({c.ram} / {c.rom}) - IMEI: {c.imei}", 'precio': float(c.precio_cliente), 'stock_max': 1})
        
    accesorios = Accesorio.query.filter(Accesorio.stock > 0, 
        (Accesorio.tipo.contains(q)) | (Accesorio.marca.contains(q)) | (Accesorio.modelo.contains(q))
    ).limit(10).all()
    for a in accesorios:
        desc = f"🎧 {a.tipo} {a.marca if a.marca else ''} {a.modelo if a.modelo else ''}"
        if a.caracteristicas: desc += f" | {a.caracteristicas.replace('|', '-')}"
        resultados.append({'id': f"ACC-{a.id}", 'tipo': 'ACCESORIO', 'descripcion': desc.strip(), 'precio': float(a.precio_cliente), 'stock_max': a.stock})
        
    repuestos = Repuesto.query.filter(Repuesto.stock > 0, 
        (Repuesto.marca.contains(q)) | (Repuesto.modelo.contains(q))
    ).limit(10).all()
    for r in repuestos:
        resultados.append({'id': f"REP-{r.id}", 'tipo': 'REPUESTO', 'descripcion': f"⚙️ {r.marca} {r.modelo} ({r.calidad})", 'precio': float(r.precio_cliente), 'stock_max': r.stock})
        
    return jsonify(resultados)

@app.route('/api/procesar_venta', methods=['POST'])
@login_requerido
def procesar_venta():
    try:
        datos = request.json
        carrito = datos.get('carrito')
        cliente_doc = datos.get('documento').strip()
        cliente_nom = datos.get('nombre').strip().upper()
        tipo_comprobante = datos.get('comprobante')
        metodo_pago = datos.get('metodo_pago')
        total = float(datos.get('total'))
        
        if not carrito or len(carrito) == 0: return jsonify({'status': 'error', 'msg': 'El carrito está vacío.'})

        nueva_venta = Venta(
            tipo_comprobante=tipo_comprobante,
            documento_cliente=cliente_doc,
            nombre_cliente=cliente_nom,
            metodo_pago=metodo_pago,
            total=total,
            personal_id=session.get('id_personal') 
        )
        db.session.add(nueva_venta)
        db.session.flush() 
        
        for item in carrito:
            tipo_prod = item['tipo'] 
            id_real = int(item['id'].split('-')[1]) 
            cantidad_vendida = int(item['cantidad'])
            
            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                tipo_producto=tipo_prod,
                producto_id=id_real,
                descripcion=item['descripcion'],
                cantidad=cantidad_vendida,
                precio_unitario=float(item['precio']),
                subtotal=float(item['precio']) * cantidad_vendida
            )
            db.session.add(detalle)
            
            if tipo_prod == 'CELULAR':
                equipo = Celular.query.get(id_real)
                if equipo and equipo.disponible: equipo.disponible = False 
                else: return jsonify({'status': 'error', 'msg': f'Celular {item["descripcion"]} no disponible.'})
            elif tipo_prod == 'ACCESORIO':
                acc = Accesorio.query.get(id_real)
                if acc and acc.stock >= cantidad_vendida: acc.stock -= cantidad_vendida
                else: return jsonify({'status': 'error', 'msg': f'Stock insuficiente para {item["descripcion"]}.'})
            elif tipo_prod == 'REPUESTO':
                rep = Repuesto.query.get(id_real)
                if rep and rep.stock >= cantidad_vendida: rep.stock -= cantidad_vendida
                else: return jsonify({'status': 'error', 'msg': f'Stock insuficiente para {item["descripcion"]}.'})
        
        db.session.commit()
        return jsonify({'status': 'success', 'msg': '¡Venta procesada y stock descontado!', 'venta_id': nueva_venta.id})
    except Exception as e:
        db.session.rollback() 
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error interno: {str(e)}'})

# ==========================================
# 12. GENERACIÓN DE COMPROBANTES (TICKETS)
# ==========================================
@app.route('/ticket_venta/<int:id_venta>')
@login_requerido
def ticket_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    detalles = DetalleVenta.query.filter_by(venta_id=venta.id).all()
    cajero = Personal.query.get(venta.personal_id)
    
    return render_template('ticket_venta.html', venta=venta, detalles=detalles, cajero=cajero)

# ==========================================
# 13. MÓDULO DE SERVICIO TÉCNICO
# ==========================================
@app.route('/servicio_tecnico')
@login_requerido
def servicio_tecnico():
    ordenes = OrdenServicio.query.order_by(OrdenServicio.fecha_ingreso.desc()).all()
    return render_template('servicio_tecnico.html', ordenes=ordenes)

@app.route('/nueva_orden')
@login_requerido
def nueva_orden():
    return render_template('form_orden.html')

@app.route('/api/guardar_orden', methods=['POST'])
@login_requerido
def guardar_orden():
    try:
        datos = request.json
        
        mano_obra = float(datos.get('mano_obra', 0))
        acuenta = float(datos.get('acuenta', 0))
        repuestos = datos.get('repuestos', [])
        total_repuestos = sum(float(r['precio']) * int(r['cantidad']) for r in repuestos)
        total_general = mano_obra + total_repuestos
        saldo = total_general - acuenta
        
        nueva_orden = OrdenServicio(
            documento_cliente=datos.get('documento').strip(),
            nombre_cliente=datos.get('nombre').strip().upper(),
            telefono_cliente=datos.get('telefono').strip(),
            marca=datos.get('marca').strip().upper(),
            modelo=datos.get('modelo').strip().upper(),
            imei_serie=datos.get('imei').strip(),
            patron_contrasena=datos.get('patron').strip(),
            falla_reportada=datos.get('falla').strip().upper(),
            costo_mano_obra=mano_obra, total=total_general,
            acuenta=acuenta, saldo=saldo, personal_id=session.get('id_personal')
        )
        db.session.add(nueva_orden)
        db.session.flush()
        
        for r in repuestos:
            id_real = int(r['id'].split('-')[1])
            cant = int(r['cantidad'])
            
            det = DetalleOrdenRepuesto(
                orden_id=nueva_orden.id, repuesto_id=id_real, descripcion=r['descripcion'],
                cantidad=cant, precio_unitario=float(r['precio']), subtotal=float(r['precio']) * cant
            )
            db.session.add(det)
            
            if r['tipo'] == 'REPUESTO':
                rep_db = Repuesto.query.get(id_real)
                if rep_db and rep_db.stock >= cant: rep_db.stock -= cant
                else: return jsonify({'status': 'error', 'msg': f'Stock insuficiente para {r["descripcion"]}'})
            elif r['tipo'] == 'ACCESORIO':
                acc_db = Accesorio.query.get(id_real)
                if acc_db and acc_db.stock >= cant: acc_db.stock -= cant
                else: return jsonify({'status': 'error', 'msg': f'Stock insuficiente para {r["descripcion"]}'})
                
        db.session.commit()
        return jsonify({'status': 'success', 'msg': 'Orden de Servicio registrada con éxito.', 'orden_id': nueva_orden.id})
        
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error interno: {str(e)}'})

@app.route('/api/actualizar_estado_orden', methods=['POST'])
@login_requerido
def actualizar_estado_orden():
    try:
        datos = request.json
        orden_id = datos.get('orden_id')
        nuevo_estado = datos.get('nuevo_estado')
        
        orden = OrdenServicio.query.get(orden_id)
        if not orden: return jsonify({'status': 'error', 'msg': 'Orden no encontrada.'})
        
        orden.estado = nuevo_estado
        
        if nuevo_estado == 'ENTREGADO':
            orden.acuenta = orden.total
            orden.saldo = 0.00
            
        db.session.commit()
        return jsonify({'status': 'success', 'msg': f'El estado se actualizó a {nuevo_estado}.'})
        
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'status': 'error', 'msg': f'Error interno: {str(e)}'})

@app.route('/ticket_orden/<int:id_orden>')
@login_requerido
def ticket_orden(id_orden):
    orden = OrdenServicio.query.get_or_404(id_orden)
    detalles = DetalleOrdenRepuesto.query.filter_by(orden_id=orden.id).all()
    tecnico = Personal.query.get(orden.personal_id)
    
    return render_template('ticket_orden.html', orden=orden, detalles=detalles, tecnico=tecnico)

# ==========================================
# 14. MÓDULO DE PEDIDOS (EN CONSTRUCCIÓN)
# ==========================================
@app.route('/pedidos')
@login_requerido
def pedidos():
    return render_template('pedidos.html')

# ==========================================
# 15. MÓDULO DE REPORTES (SOLO ADMINISTRADOR)
# ==========================================
@app.route('/reportes')
@admin_requerido
def reportes():
    ventas = Venta.query.order_by(Venta.fecha_hora.desc()).all()
    ordenes = OrdenServicio.query.order_by(OrdenServicio.fecha_ingreso.desc()).all()
    
    return render_template('reportes.html', ventas=ventas, ordenes=ordenes)

# ==========================================
# 11. CONSTRUCCIÓN AUTOMÁTICA DE LA BD
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        inicializar_catalogo()
    app.run(debug=True, port=5000)