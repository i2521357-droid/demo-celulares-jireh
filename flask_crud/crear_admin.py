from app import app, db, Rol, Personal, bcrypt

with app.app_context():
    # Verificamos si los roles ya existen para no duplicarlos
    if not Rol.query.first():
        # 1. Crear los roles base
        rol_admin = Rol(nombre="ADMINISTRADOR")
        rol_trabajador = Rol(nombre="TRABAJADOR")
        db.session.add_all([rol_admin, rol_trabajador])
        db.session.commit()
        
        # 2. Crear tu usuario administrador con la clave por defecto
        hashed_password = bcrypt.generate_password_hash('123456').decode('utf-8')
        admin_user = Personal(
            nombres="Daniel", 
            apellidos="Diaz", 
            usuario="admin", 
            password_hash=hashed_password, 
            rol_id=rol_admin.id
        )
        db.session.add(admin_user)
        db.session.commit()
        
        print("¡Inyección exitosa! Base de datos lista.")
        print("Usuario: admin | Contraseña: 123456")
    else:
        print("La base de datos ya tiene roles y usuarios registrados.")