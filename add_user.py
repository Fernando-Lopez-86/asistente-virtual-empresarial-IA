from modules.database import create_database, add_user

# Crear la base de datos si no existe
create_database()

# Agregar un usuario nuevo
username = ""
password = ""
role = ""  # o cualquier otro rol que necesites

add_user(username, password, role)
print(f"Usuario {username} agregado correctamente con el rol {role}.")