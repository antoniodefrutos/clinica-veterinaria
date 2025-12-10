# Proyecto Clínica Veterinaria – Documentación General #
## 1. Descripción General
Este proyecto implementa un sistema completo para la gestión de una clínica veterinaria,
compuesto por:
- **Backend (FastAPI + SQLite)**
- **Frontend (Streamlit)**
- **Autenticación JWT**
- **Panel de análisis con gráficos**
- **CRUD de clientes, mascotas, citas y facturación (roles Admin/Recepcionista)**
El objetivo es disponer de un sistema funcional para administración de datos clínicos, control de
citas, historial médico, facturas y métricas de negocio.
---
## 2. Arquitectura del Proyecto
El proyecto está dividido en dos módulos principales:
### 2.1 Backend (carpeta `/backend`)
Implementado con **FastAPI**, proporciona:
- Endpoints REST para CRUD de:
- Clientes
- Mascotas
- Citas
- Facturas
- Historial médico
- Sistema de autenticación OAuth2 + JWT.
- Roles de usuario:
- **Admin** (gestiona todo, incluida la eliminación)
- **Recepcionista** (creación/edición, sin eliminar)
- Sistema de informes de ingresos.
Estructura base:
```
backend/
    app/
    main.py
    routers/
    models/
    schemas/
    utils/
    seed.py
    database.py
```
### 2.2 Frontend (carpeta `/frontend`)
Implementado con **Streamlit**, ofrece:
- Interfaz web agradable y estructurada.
- Login con almacenamiento de JWT.
- Menú de navegación centrado en la parte superior.
- Módulos:
- Gestión de clientes
- Gestión de mascotas
- Gestión de citas
- Facturación
- Análisis con gráficos interactivos (Plotly)
---
## 3. Instalación
### 3.1 Requisitos
- Python 3.10+
- pip
- Git
### 3.2 Instalación del Backend
```
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 
```
### 3.3 Instalación del Frontend
```
cd frontend
pip install -r requirements.txt
streamlit run main.py
```
---
## 4. Autenticación y Roles
### 4.1 Login
El frontend solicita:
- Email
- Contraseña
El backend devuelve un **JWT**, que se guarda internamente para permitir el acceso a los
distintos módulos.
### 4.2 Roles
| Rol  |                  Permisos              |
|------|----------------------------------------|
| Administrador |  CRUD completo, incluyendo eliminación |
| Recepcionista |  Crear / editar, sin eliminar |
---
## 5. Funcionalidades
### 5.1 Gestión de Clientes
- Crear clientes (incluye teléfono)
- Listado de clientes
- Edición
- Eliminación (solo admin)
- Visualización de mascotas asociadas
### 5.2 Gestión de Mascotas
- Crear mascotas
- Listado y detalle
- Eliminación (solo admin)
### 5.3 Citas
- Crear cita
- Listado por cliente o general
- Edición
- Eliminación disponible según permisos
### 5.4 Facturación
- Crear facturas
- Listar facturas
- Marcar como pagadas
- Asociación a cliente/mascota/cita
### 5.5 Análisis
Incluye gráficos como:
- **Ingresos por fecha**
- **Número de citas por mes**
- **Mascotas registradas por tipo**
- **Clientes nuevos por periodo**
---
## 6. Endpoints Principales (resumen)
### 6.1 Autenticación
- `POST /auth/token`
- `POST /auth/register`
### 6.2 Clientes
- `GET /clientes/`
- `POST /clientes/`
- `PUT /clientes/{id}`
- `DELETE /clientes/{id}` (solo admin)
### 6.3 Mascotas
- `GET /mascotas/`
- `POST /mascotas/`
- `DELETE /mascotas/{id}` (solo admin)
### 6.4 Citas
- `GET /citas/`
- `POST /citas/`
- `DELETE /citas/{id}` (según rol)
### 6.5 Facturación
- `GET /facturacion/`
- `POST /facturacion/`
- `PUT /facturacion/{id}`
### 6.6 Informes
- `GET /informes/ingresos?fecha_inicio=&fecha;_fin=`
---
## 7. Base de Datos
Modelo basado en SQLite, con tablas:
- Users
- Roles
- Clients
- Pets
- Appointments
- Invoices
- Payments
- MedicalHistory
- SubscriptionPlans
---
## 8. Ejecución del Proyecto Completo
### Paso 1: Arrancar el backend
```
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```
### Paso 2: Arrancar el frontend
```
cd frontend
streamlit run main.py
```
---

## 9. Créditos
Proyecto desarrollado como solución integral para gestión de clínicas veterinarias.