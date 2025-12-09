-- * Sistema de Gestión para Clínica veterinaria - Backend (FastAPI) * --

1. Requisitos previos:
Antes de iniciar, asegúrate de tener instalado:
 - Python 3.10+
 - pip
 - git
 - curl (para pruebas desde terminal)

2. Instalación del entorno:
Clonar el repositorio o descargar el proyecto:
    git clone https://github.com/antoniodefrutos/clinica-veterinaria.git
    cd clinica-veterinaria/backend
Crear entorno virtual:
    python3 -m venv venv
    source venv/bin/activate
Instalar dependencias:
    pip install -r requirements.txt

3. Variables necesarias:
Este backend usa una SECRET_KEY para generar y validar JWT.
    SECRET_KEY utilizada en la práctica: "malaspulgas"
    Está declarada dentro del archivo "security.py".

4. Base de datos:
Antes de arrancar el servidor, ejecutar:
    python seed.py
Esto crea:
    - Usuarios (admin y recepcionista)
    - Clientes
    - Mascotas
    - Citas
    - Facturas y pagos

5. Arrancar el servidor:
Desde el directorio backend:
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
La API está disponible en:
    http://127.0.0.1:8000
Documentación Swagger:
    http://127.0.0.1:8000/docs

6. Autenticación:
    - Login (Obtener token JWT):
        Admin: ------ email: admin@example.com
               ------ password: admin123
        Recepcionista: ----- email: recep@example.com
                       ----- password: recep123
    Ejemplo Login: 
    curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"


7. Endpoints principales:
    
    - Clientes:
        * Crear: curl -X POST http://127.0.0.1:8000/clientes \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{"name":"Juan Pérez","email":"juan@example.com","phone":"123456789"}'
        * Listar: curl -X GET http://127.0.0.1:8000/clientes \
-H "Authorization: Bearer $TOKEN"


    - Mascotas: 
        * Crear: curl -X POST http://127.0.0.1:8000/mascotas \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{"name":"Firulais","species":"Perro","age":5,"owner_id":1}'

    - Citas:
        * Crear: curl -X POST http://127.0.0.1:8000/citas \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{"pet_id":1,"date":"2025-12-01T10:00:00","reason":"Revisión"}'
        * Listar: curl -X GET http://127.0.0.1:8000/citas \
-H "Authorization: Bearer $TOKEN"

    - Facturación:
        * Crear factura: curl -X POST http://127.0.0.1:8000/facturacion \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{"appointment_id":1,"amount":80.0}'
        * Registrar pago: curl -X POST http://127.0.0.1:8000/facturacion/pagar \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{"invoice_id":1,"amount":80.0,"method":"tarjeta"}'

    - Informes:
        * Ingresos por rango de fechas: curl -X GET "http://127.0.0.1:8000/informes/ingresos?start_date=2025-01-01&end_date=2025-12-31" \
-H "Authorization: Bearer $TOKEN"


8. Estructura del proyecto:

backend/
│
├── app/
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── utils/
│   └── database.py
│
├── seed.py
├── requirements.txt
└── README.md


9. Usuarios del sistema:

    ROL:                EMAIL:              CONTRASEÑA:

- Administrador ----- admin@example.es -----  admin123

- Recepcionista ----- recep@example.es -----  recep123


10. Notas finales:

- El sistema cumple todos los requirimientos del proyecto.
- Toda la API requiere autentificación excepto el login.
- El rol Admin. es obligatorio para acceder a los informes.
- El seed.py genera datos listos para hacer pruebas rápidas con curl.