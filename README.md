# Sistema de Gestión de Tareas

## Descripción

Sistema web para gestión de tareas desarrollado con Flask, SQLite y Bootstrap. Permite a los usuarios registrarse, crear, asignar, filtrar y gestionar tareas con diferentes prioridades y estados.

## Características Principales

### Autenticación y Perfiles
- ✅ Registro de usuarios con validación
- ✅ Inicio y cierre de sesión seguro
- ✅ Gestión de perfiles (editar nombre y email)
- ✅ Cambio de contraseña con validaciones
- ✅ Roles de usuario (usuario/admin)

### Gestión de Tareas
- ✅ Crear, editar y eliminar tareas
- ✅ Asignar tareas a usuarios (admin)
- ✅ Marcar tareas como completadas/pendientes
- ✅ Establecer prioridades (alta, media, baja)
- ✅ Fechas límite con indicador de vencimiento
- ✅ Búsqueda por texto en título y descripción
- ✅ Filtros por estado, prioridad y asignado

### Autorización y Seguridad
- ✅ Control de acceso basado en roles
- ✅ Protección CSRF en formularios
- ✅ Hash seguro de contraseñas
- ✅ Validaciones robustas de entrada
- ✅ Sesiones seguras

### Interfaz de Usuario
- ✅ Diseño responsivo con Bootstrap 5
- ✅ Dashboard con estadísticas
- ✅ Navegación intuitiva
- ✅ Mensajes de éxito/error
- ✅ Confirmaciones para acciones destructivas

## Tecnologías Utilizadas

### Backend
- **Flask 2.3.3** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos
- **Werkzeug** - Utilidades y seguridad
- **WTForms** - Validación de formularios

### Frontend
- **Jinja2** - Motor de plantillas
- **Bootstrap 5** - Framework CSS
- **Font Awesome** - Iconos
- **JavaScript** - Interactividad

### Pruebas
- **pytest** - Framework de pruebas
- **pytest-flask** - Pruebas de integración
- **pytest-cov** - Cobertura de código
- **Selenium** - Pruebas de aceptación

## Estructura del Proyecto

```
Sistema-de-Gestion-de-Tareas/
│
├── app/                          # Aplicación principal
│   ├── __init__.py              # Configuración de la app
│   ├── models.py                # Modelos de base de datos
│   ├── forms.py                 # Formularios WTF
│   ├── main_routes.py           # Rutas principales
│   │
│   ├── auth/                    # Módulo de autenticación
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── tasks/                   # Módulo de tareas
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── services/                # Servicios de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── task_service.py
│   │
│   ├── templates/               # Plantillas Jinja
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   └── tasks/
│   │
│   └── static/                  # Archivos estáticos
│       ├── css/
│       └── js/
│
├── tests/                       # Pruebas
│   ├── unit/                   # Pruebas unitarias
│   ├── integration/            # Pruebas de integración
│   └── acceptance/             # Pruebas de aceptación
│
├── instance/                   # Base de datos SQLite
├── htmlcov/                   # Reportes de cobertura
├── config.py                  # Configuración
├── run.py                     # Punto de entrada
├── requirements.txt           # Dependencias
└── README.md                  # Este archivo
```

## Instalación y Configuración

### Prerequisitos
- Python 3.8+
- Git
- Chrome/Chromium (para pruebas de aceptación)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/usuario/Sistema-de-Gestion-de-Tareas.git
cd Sistema-de-Gestion-de-Tareas
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional)**
```bash
# Windows
set SECRET_KEY=tu-clave-secreta-aqui
set DATABASE_URL=sqlite:///instance/tasks.db

# Linux/Mac
export SECRET_KEY=tu-clave-secreta-aqui
export DATABASE_URL=sqlite:///instance/tasks.db
```

## Uso

### Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en http://localhost:5000

### Usuarios por defecto

- **Admin**: admin@example.com / admin123
- Puedes crear nuevos usuarios desde la página de registro

### Funcionalidades principales

1. **Registro e inicio de sesión**
   - Accede a `/auth/register` para crear una cuenta
   - Inicia sesión en `/auth/login`

2. **Dashboard**
   - Vista principal con estadísticas de tareas
   - Acceso rápido a tareas recientes

3. **Gestión de tareas**
   - Crear: `/tasks/new`
   - Listar: `/tasks/`
   - Editar: Desde la lista de tareas
   - Filtrar: Usa los controles de filtro en la lista

4. **Perfil de usuario**
   - Editar perfil: `/auth/profile`
   - Cambiar contraseña: `/auth/change_password`

## Pruebas

### Ejecutar todas las pruebas
```bash
pytest
```

### Ejecutar por tipo de prueba
```bash
# Pruebas unitarias
pytest tests/unit/

# Pruebas de integración
pytest tests/integration/

# Pruebas de aceptación (requiere Chrome)
pytest tests/acceptance/
```

### Generar reporte de cobertura
```bash
pytest --cov=app --cov-report=html
```

El reporte se genera en `htmlcov/index.html`

### Usando Makefile
```bash
# Ver comandos disponibles
make help

# Instalar dependencias
make install

# Ejecutar aplicación
make run

# Ejecutar todas las pruebas
make test

# Ejecutar con cobertura
make test-coverage
```

## Base de Datos

### Modelo de datos

**Tabla `users`:**
- `id` (INTEGER, PRIMARY KEY)
- `name` (VARCHAR(100), NOT NULL)
- `email` (VARCHAR(120), UNIQUE, NOT NULL)
- `password_hash` (VARCHAR(255), NOT NULL)
- `role` (VARCHAR(20), DEFAULT 'user')
- `created_at` (DATETIME, DEFAULT NOW)

**Tabla `tasks`:**
- `id` (INTEGER, PRIMARY KEY)
- `title` (VARCHAR(200), NOT NULL)
- `description` (TEXT)
- `status` (VARCHAR(20), DEFAULT 'pending')
- `priority` (VARCHAR(20), DEFAULT 'medium')
- `due_date` (DATE)
- `created_by` (INTEGER, FOREIGN KEY → users.id)
- `assigned_to` (INTEGER, FOREIGN KEY → users.id)
- `created_at` (DATETIME, DEFAULT NOW)
- `updated_at` (DATETIME, DEFAULT NOW)

### Índices

- `users.email` (único)
- `tasks.title`
- `tasks.assigned_to, tasks.status` (compuesto)
- `tasks.due_date, tasks.status` (compuesto)

## API Endpoints

### Autenticación
- `GET/POST /auth/register` - Registro de usuario
- `GET/POST /auth/login` - Inicio de sesión
- `GET /auth/logout` - Cerrar sesión
- `GET/POST /auth/profile` - Gestión de perfil
- `GET/POST /auth/change_password` - Cambio de contraseña

### Tareas
- `GET /tasks/` - Listar tareas (con filtros)
- `GET/POST /tasks/new` - Crear tarea
- `GET/POST /tasks/<id>/edit` - Editar tarea
- `POST /tasks/<id>/delete` - Eliminar tarea
- `POST /tasks/<id>/toggle` - Cambiar estado
- `GET /tasks/<id>` - Ver detalle

### Principal
- `GET /` - Dashboard
- `GET /dashboard` - Redirige al dashboard

## Seguridad

### Medidas implementadas

1. **Autenticación segura**
   - Hash de contraseñas con Werkzeug
   - Sesiones con expiración
   - Validación de fortaleza de contraseñas

2. **Autorización**
   - Control de acceso basado en roles
   - Verificación de permisos en cada endpoint
   - Aislamiento de datos por usuario

3. **Protección de formularios**
   - Tokens CSRF en todos los formularios
   - Validación server-side
   - Sanitización de entrada

4. **Configuración segura**
   - Secret key configurable
   - Headers de seguridad
   - Configuración de producción

## Desarrollo

### Convenciones de código

- **PEP 8** para estilo de Python
- **Nombres descriptivos** para variables y funciones
- **Docstrings** para métodos públicos
- **Comentarios** solo cuando sea necesario

### Estructura de pruebas

1. **Unitarias** (`tests/unit/`)
   - Servicios de negocio
   - Modelos de datos
   - Utilidades

2. **Integración** (`tests/integration/`)
   - Rutas y endpoints
   - Integración con base de datos
   - Flujos completos

3. **Aceptación** (`tests/acceptance/`)
   - Flujos de usuario end-to-end
   - Interfaz de usuario
   - Casos de uso reales

### Contribuir

1. Fork del repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit de cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Deployment

### Producción

Para deployment en producción:

1. **Configurar variables de entorno**
```bash
export FLASK_ENV=production
export SECRET_KEY=clave-muy-segura-aleatoria
export DATABASE_URL=sqlite:///prod_tasks.db
```

2. **Instalar dependencias de producción**
```bash
pip install -r requirements.txt
```

3. **Usar servidor WSGI**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Docker (opcional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## Soporte

Para reportar bugs o solicitar características:

1. Crear issue en GitHub
2. Incluir información del entorno
3. Pasos para reproducir el problema
4. Logs de error si aplica

## Changelog

### v1.0.0 (2024-01-XX)
- ✅ Sistema de autenticación completo
- ✅ CRUD de tareas con autorización
- ✅ Búsqueda y filtrado avanzado
- ✅ Dashboard con estadísticas
- ✅ Interfaz responsiva
- ✅ Suite completa de pruebas
- ✅ Documentación completa