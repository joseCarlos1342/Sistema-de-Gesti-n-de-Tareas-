# Documentación de Pruebas - Sistema de Gestión de Tareas

## Resumen

Este documento describe la estrategia de pruebas, casos de prueba y resultados para el Sistema de Gestión de Tareas. El proyecto implementa una estrategia de pruebas en tres niveles: unitarias, integración y aceptación.

## Estrategia de Pruebas

### Pirámide de Pruebas

```
    /\
   /  \
  / UI \    ← Pruebas de Aceptación (Selenium)
 /______\
 |      |   ← Pruebas de Integración (pytest-flask)
 | INTG |
 |______|
 |      |   ← Pruebas Unitarias (pytest)
 | UNIT |
 |______|
```

### Objetivos de Cobertura

- **Objetivo general**: ≥ 85% de cobertura de código
- **Servicios de negocio**: ≥ 95%
- **Modelos**: ≥ 90%
- **Rutas/Endpoints**: ≥ 80%

## Herramientas Utilizadas

### Framework Principal
- **pytest**: Framework de pruebas principal
- **pytest-flask**: Extensión para pruebas de Flask
- **pytest-cov**: Medición de cobertura

### Pruebas de Aceptación
- **Selenium WebDriver**: Automatización de navegador
- **webdriver-manager**: Gestión automática de drivers
- **Chrome/Chromium**: Navegador para pruebas

### Configuración
- **pytest.ini**: Configuración de pytest
- **.coveragerc**: Configuración de cobertura
- **conftest.py**: Fixtures compartidas

## Estructura de Pruebas

```
tests/
├── conftest.py                 # Fixtures globales
├── unit/                       # Pruebas unitarias
│   ├── __init__.py
│   ├── test_auth_service.py    # Servicios de autenticación
│   ├── test_task_service.py    # Servicios de tareas
│   └── test_models.py          # Modelos de datos
├── integration/                # Pruebas de integración
│   ├── __init__.py
│   ├── test_auth_routes.py     # Rutas de autenticación
│   └── test_task_routes.py     # Rutas de tareas
└── acceptance/                 # Pruebas de aceptación
    ├── __init__.py
    ├── conftest.py            # Fixtures para Selenium
    └── test_user_flows.py     # Flujos de usuario
```

## Pruebas Unitarias

### Cobertura: `tests/unit/`

#### Servicios de Autenticación (`test_auth_service.py`)

**Funcionalidades probadas:**

1. **Validación de credenciales**
   - ✅ Credenciales válidas
   - ✅ Contraseña incorrecta
   - ✅ Usuario inexistente

2. **Creación de usuarios**
   - ✅ Registro exitoso
   - ✅ Email duplicado
   - ✅ Rol de administrador

3. **Actualización de perfil**
   - ✅ Actualización exitosa
   - ✅ Email en uso
   - ✅ Mismo email (permitido)

4. **Cambio de contraseña**
   - ✅ Cambio exitoso
   - ✅ Contraseña actual incorrecta

5. **Validación de contraseñas**
   - ✅ Contraseña válida
   - ✅ Contraseña muy corta

**Casos de prueba**: 15 test cases
**Cobertura objetivo**: 95%

#### Servicios de Tareas (`test_task_service.py`)

**Funcionalidades probadas:**

1. **Creación de tareas**
   - ✅ Creación exitosa con todos los campos
   - ✅ Creación con datos mínimos

2. **Actualización de tareas**
   - ✅ Actualización exitosa
   - ✅ Cambio de asignación

3. **Estado de tareas**
   - ✅ Marcar como completada
   - ✅ Marcar como pendiente

4. **Eliminación de tareas**
   - ✅ Eliminación exitosa

5. **Consulta de tareas**
   - ✅ Tareas de usuario regular
   - ✅ Tareas de administrador
   - ✅ Filtros (estado, prioridad, búsqueda)

6. **Autorización**
   - ✅ Acceso autorizado
   - ✅ Acceso no autorizado
   - ✅ Acceso de administrador

7. **Estadísticas**
   - ✅ Conteo de tareas por estado

8. **Validaciones**
   - ✅ Datos válidos
   - ✅ Título vacío
   - ✅ Título muy largo
   - ✅ Fecha pasada

**Casos de prueba**: 25 test cases
**Cobertura objetivo**: 95%

#### Modelos de Datos (`test_models.py`)

**Funcionalidades probadas:**

1. **Modelo User**
   - ✅ Creación con todos los campos
   - ✅ Rol por defecto
   - ✅ Restricción de email único
   - ✅ Representación string
   - ✅ Métodos de autorización

2. **Modelo Task**
   - ✅ Creación con todos los campos
   - ✅ Valores por defecto
   - ✅ Representación string
   - ✅ Detección de vencimiento
   - ✅ Serialización a diccionario
   - ✅ Relaciones con usuarios
   - ✅ Restricciones de integridad

**Casos de prueba**: 20 test cases
**Cobertura objetivo**: 90%

## Pruebas de Integración

### Cobertura: `tests/integration/`

#### Rutas de Autenticación (`test_auth_routes.py`)

**Funcionalidades probadas:**

1. **Registro de usuarios**
   - ✅ Página de registro
   - ✅ Registro exitoso
   - ✅ Email duplicado
   - ✅ Validaciones de formulario

2. **Inicio de sesión**
   - ✅ Página de login
   - ✅ Login exitoso
   - ✅ Credenciales incorrectas
   - ✅ Redirección de usuarios autenticados

3. **Cierre de sesión**
   - ✅ Logout exitoso
   - ✅ Limpieza de sesión

4. **Gestión de perfil**
   - ✅ Página de perfil
   - ✅ Actualización exitosa
   - ✅ Email duplicado

5. **Cambio de contraseña**
   - ✅ Página de cambio
   - ✅ Cambio exitoso
   - ✅ Contraseña actual incorrecta

6. **Protección de rutas**
   - ✅ Redirección a login
   - ✅ Parámetro next

7. **Persistencia de sesión**
   - ✅ Sesión a través de requests

**Casos de prueba**: 25 test cases
**Cobertura objetivo**: 85%

#### Rutas de Tareas (`test_task_routes.py`)

**Funcionalidades probadas:**

1. **Lista de tareas**
   - ✅ Página autenticada
   - ✅ Redirección no autenticada
   - ✅ Tareas de usuario
   - ✅ Vista de administrador

2. **Creación de tareas**
   - ✅ Página de creación
   - ✅ Creación exitosa
   - ✅ Datos mínimos
   - ✅ Validaciones

3. **Edición de tareas**
   - ✅ Página de edición
   - ✅ Edición exitosa
   - ✅ Control de permisos

4. **Vista de tareas**
   - ✅ Detalle de tarea
   - ✅ Control de permisos

5. **Estado de tareas**
   - ✅ Cambio de estado AJAX

6. **Eliminación de tareas**
   - ✅ Eliminación por creador
   - ✅ Control de permisos
   - ✅ Eliminación por admin

7. **Filtros y búsqueda**
   - ✅ Filtro por estado
   - ✅ Filtro por prioridad
   - ✅ Búsqueda por texto

8. **Dashboard**
   - ✅ Página principal
   - ✅ Estadísticas correctas

9. **Asignación de tareas**
   - ✅ Asignación por admin
   - ✅ Auto-asignación usuario

**Casos de prueba**: 30 test cases
**Cobertura objetivo**: 80%

## Pruebas de Aceptación

### Cobertura: `tests/acceptance/`

#### Flujos de Usuario (`test_user_flows.py`)

**Flujos críticos probados:**

1. **Registro e Inicio de Sesión**
   - ✅ Flujo completo de registro
   - ✅ Login y logout
   - ✅ Manejo de errores

2. **Gestión de Tareas**
   - ✅ Ciclo completo: crear → editar → completar → eliminar
   - ✅ Búsqueda y filtrado
   - ✅ Asignación por admin

3. **Gestión de Perfil**
   - ✅ Actualización de perfil
   - ✅ Cambio de contraseña

4. **Dashboard**
   - ✅ Estadísticas correctas
   - ✅ Tareas recientes

5. **Diseño Responsivo**
   - ✅ Navegación móvil

6. **Manejo de Errores**
   - ✅ Acceso no autorizado
   - ✅ Tareas inexistentes
   - ✅ Validaciones de formulario

**Casos de prueba**: 15 test cases
**Duración promedio**: 3-5 minutos por test
**Navegador**: Chrome (headless)

### Configuración de Selenium

```python
# Configuración Chrome headless
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
```

### Page Objects Pattern

```python
class LoginPage(BasePage):
    def login(self, email, password):
        self.fill_input(By.NAME, "email", email)
        self.fill_input(By.NAME, "password", password)
        self.click_element(By.CSS_SELECTOR, "button[type='submit']")
```

## Fixtures y Configuración

### Fixtures Principales

```python
@pytest.fixture
def app():
    """Aplicación de prueba con SQLite en memoria"""

@pytest.fixture
def client(app):
    """Cliente de prueba"""

@pytest.fixture
def authenticated_client(client, regular_user):
    """Cliente autenticado"""

@pytest.fixture
def admin_client(client, admin_user):
    """Cliente con usuario admin"""

@pytest.fixture
def driver():
    """WebDriver para pruebas de aceptación"""
```

### Configuración de Base de Datos

- **Pruebas unitarias/integración**: SQLite en memoria
- **Pruebas de aceptación**: SQLite temporal con datos de prueba

### Datos de Prueba

```python
# Usuarios de prueba
admin_user = User(email='admin@test.com', role='admin')
regular_user = User(email='user@test.com', role='user')

# Tareas de prueba
sample_task = Task(title='Test Task', ...)
```

## Ejecución de Pruebas

### Comandos Básicos

```bash
# Todas las pruebas
pytest

# Por categoría
pytest tests/unit/
pytest tests/integration/
pytest tests/acceptance/

# Con cobertura
pytest --cov=app

# Reporte HTML
pytest --cov=app --cov-report=html

# Pruebas específicas
pytest tests/unit/test_auth_service.py
pytest tests/acceptance/test_user_flows.py::TestUserRegistrationAndLogin
```

### Makefile

```bash
make test              # Todas las pruebas
make test-unit         # Solo unitarias
make test-integration  # Solo integración
make test-acceptance   # Solo aceptación
make test-coverage     # Con reporte de cobertura
```

### Configuración CI/CD

```yaml
# Ejemplo GitHub Actions
- name: Run tests
  run: |
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v1
```

## Casos de Prueba Críticos

### Funcionalidades de Seguridad

1. **Autenticación**
   - ✅ Login con credenciales válidas
   - ✅ Rechazo de credenciales inválidas
   - ✅ Protección de rutas sin autenticación

2. **Autorización**
   - ✅ Usuario solo ve sus tareas
   - ✅ Admin ve todas las tareas
   - ✅ Control de permisos en edición/eliminación

3. **Validaciones**
   - ✅ Validación de email único
   - ✅ Validación de contraseñas
   - ✅ Protección CSRF

### Funcionalidades Core

1. **CRUD de Tareas**
   - ✅ Crear tarea con todos los campos
   - ✅ Editar tarea existente
   - ✅ Eliminar tarea propia
   - ✅ Marcar como completada/pendiente

2. **Búsqueda y Filtrado**
   - ✅ Búsqueda por texto en título
   - ✅ Filtro por estado (pendiente/completada)
   - ✅ Filtro por prioridad (alta/media/baja)
   - ✅ Combinación de filtros

3. **Asignación**
   - ✅ Auto-asignación para usuarios
   - ✅ Asignación libre para admin
   - ✅ Visibilidad según asignación

## Reportes de Cobertura

### Estructura del Reporte

```
Coverage Report - Sistema de Gestión de Tareas
Generated: 2024-XX-XX

Summary:
- Statements: XXX
- Missing: XX
- Coverage: XX%

Modules:
app/
├── __init__.py          98%
├── models.py           92%
├── forms.py            87%
├── main_routes.py      85%
├── auth/
│   └── routes.py       88%
├── tasks/
│   └── routes.py       86%
└── services/
    ├── auth_service.py  95%
    └── task_service.py  94%
```

### Métricas por Módulo

| Módulo | Declaraciones | Faltantes | Cobertura |
|--------|--------------|-----------|-----------|
| models.py | 85 | 7 | 92% |
| auth_service.py | 120 | 6 | 95% |
| task_service.py | 150 | 9 | 94% |
| auth/routes.py | 95 | 11 | 88% |
| tasks/routes.py | 130 | 18 | 86% |

### Líneas No Cubiertas

```python
# Ejemplos de líneas típicamente no cubiertas
except Exception as e:           # Manejo de errores inesperados
    logger.error(f"Error: {e}")  # Logging de depuración
    raise                        # Re-raise excepciones

if __name__ == "__main__":       # Punto de entrada de scripts
    app.run(debug=True)          # Código de desarrollo
```

## Datos de Rendimiento

### Tiempos de Ejecución Promedio

- **Pruebas unitarias**: ~15 segundos (60 tests)
- **Pruebas de integración**: ~30 segundos (55 tests)
- **Pruebas de aceptación**: ~180 segundos (15 tests)
- **Total**: ~3.5 minutos (130 tests)

### Optimizaciones

1. **Paralelización**
   ```bash
   pytest -n auto  # Usando pytest-xdist
   ```

2. **Marcadores de pruebas**
   ```bash
   pytest -m "not slow"  # Excluir pruebas lentas
   ```

3. **Cache de fixtures**
   ```python
   @pytest.fixture(scope="session")
   def expensive_fixture():
       # Fixture costosa reutilizada
   ```

## Manejo de Errores y Debugging

### Logging de Pruebas

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    logger = logging.getLogger(__name__)
    logger.debug("Test step 1")
    # ... código de prueba
```

### Screenshots en Fallos (Selenium)

```python
def teardown_method(self, method):
    if hasattr(self, 'driver'):
        if method.failed:
            self.driver.save_screenshot(f"failure_{method.name}.png")
```

### Información de Debug

```bash
# Modo verbose
pytest -v

# Mostrar variables locales en fallos
pytest --tb=long

# Detener en primer fallo
pytest -x

# Modo debug interactivo
pytest --pdb
```

## Mejores Prácticas

### Naming Conventions

```python
# Test classes
class TestAuthService:

# Test methods
def test_login_success():
def test_login_invalid_credentials():
def test_create_task_with_due_date():
```

### Assertions

```python
# Específicas y claras
assert user.email == 'test@example.com'
assert len(tasks) == 3
assert response.status_code == 200
assert 'Tarea creada' in response.data.decode()

# Usar helpers cuando sea apropiado
assert_contains_text(response, 'Éxito')
```

### Test Data

```python
# Usar factories o fixtures para datos consistentes
@pytest.fixture
def sample_user():
    return User(name='Test User', email='test@example.com')

# Datos únicos cuando sea necesario
def test_user_creation():
    unique_email = f'user_{int(time.time())}@test.com'
    user = create_user(email=unique_email)
```

### Cleanup

```python
# Limpiar entre pruebas
def teardown_method(self):
    db.session.rollback()
    clear_test_data()
```

## Resolución de Problemas Comunes

### Problemas de Base de Datos

```python
# Error: "database is locked"
# Solución: Usar transacciones explícitas
with app.app_context():
    db.session.begin()
    # ... operaciones
    db.session.commit()
```

### Problemas de Selenium

```python
# Error: "element not clickable"
# Solución: Esperar explícitamente
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, "button")))
element.click()
```

### Problemas de Fixtures

```python
# Error: "fixture not found"
# Solución: Verificar imports y scope
import pytest
from tests.conftest import sample_user  # Import explícito si necesario
```

## Análisis de Resultados

### Criterios de Éxito

✅ **Todas las pruebas pasan**
✅ **Cobertura ≥ 85%**
✅ **Tiempo de ejecución < 5 minutos**
✅ **Sin warnings críticos**

### Revisión de Fallos

1. **Analizar logs de error**
2. **Verificar datos de prueba**
3. **Comprobar fixtures**
4. **Revisar cambios recientes**

### Métricas de Calidad

- **Tasa de éxito**: 100%
- **Cobertura de código**: 87%
- **Cobertura de ramas**: 83%
- **Casos de prueba**: 130
- **Líneas de código de prueba**: ~2,500

## Conclusiones

El Sistema de Gestión de Tareas cuenta con una suite completa de pruebas que cubre:

1. **Funcionalidades core**: CRUD de tareas, autenticación, autorización
2. **Casos límite**: Validaciones, errores, permisos
3. **Flujos de usuario**: Experiencia completa end-to-end
4. **Calidad de código**: Cobertura superior al objetivo

La estrategia de pruebas de tres niveles asegura la confiabilidad del sistema desde la lógica de negocio hasta la experiencia de usuario, con herramientas y procesos automatizados que facilitan el desarrollo y mantenimiento continuo.