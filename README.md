# 🏪 El Almacén

<div align="center">
  <img src="static/images/el_almacen_logo.png" alt="El Almacén Logo" width="200"/>
  
  *Sistema moderno de gestión de almacenes y ventas*
</div>

---

## ✨ Características Principales

## ✨ Características Principales

### 👥 Gestión de Usuarios
- Sistema de autenticación con roles (Administrador, Cajero)
- Control de acceso basado en roles
- Panel de administración personalizado

### 📦 Gestión de Productos
- CRUD completo de productos
- Sistema de categorías
- Búsqueda avanzada de productos
- Control de stock en tiempo real
- Alertas de stock bajo

### 👥 Gestión de Clientes
- Base de datos de clientes
- Sistema de cuentas corrientes
- Historial de compras por cliente

### 💰 Sistema de Ventas
- Interfaz intuitiva para cajeros
- Generación automática de tickets
- Control de ventas fiadas
- Estadísticas de ventas en tiempo real

### 📊 Dashboard Administrativo
- Métricas clave del negocio
- Gráficos interactivos con Chart.js
- Vista general del inventario
- Reportes de ventas y productos más vendidos

### 🎨 Interfaz Moderna
- Diseño glassmorphism
- Interfaz responsive
- Tema oscuro con efectos visuales modernos
- Iconografía SVG personalizada

## 📸 Capturas de Pantalla

> **Nota**: Las capturas de pantalla deben colocarse en la carpeta `docs/screenshots/` del repositorio.

### Dashboard Administrativo
<div align="center">
  <img src="docs/screenshots/dashboard-admin.png" alt="Dashboard Administrativo" width="800"/>
  <p><em>Vista general con métricas, gráficos y acciones rápidas</em></p>
</div>

### Gestión de Productos
<div align="center">
  <img src="docs/screenshots/lista-productos.png" alt="Lista de Productos" width="800"/>
  <p><em>Interfaz de búsqueda y gestión de inventario</em></p>
</div>

### Sistema de Ventas
<div align="center">
  <img src="docs/screenshots/nueva-venta.png" alt="Nueva Venta" width="800"/>
  <p><em>Interfaz intuitiva para cajeros</em></p>
</div>

## �🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.7
- **Base de Datos**: PostgreSQL / SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualización**: Chart.js
- **Estilos**: CSS con efectos glassmorphism
- **Python**: 3.13.7

## 📁 Estructura del Proyecto

```
el_almacen/
├── accounts/              # Gestión de usuarios y autenticación
├── clients/               # Gestión de clientes
├── products/              # Gestión de productos y categorías
├── sales/                 # Sistema de ventas y tickets
├── cuentas_corrientes/    # Sistema de cuentas corrientes
├── dashboards/            # Dashboards administrativos
├── reports/               # Sistema de reportes
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── templates/             # Plantillas HTML
├── media/                 # Archivos multimedia subidos
├── el_almacen/            # Configuración principal del proyecto
├── manage.py
└── requirements.txt
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.13.7
- PostgreSQL (opcional, por defecto usa SQLite)
- Git

### Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/NicoButter/el_almacen.git
   cd el_almacen
   ```

2. **Crea un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura la base de datos:**
   ```bash
   python manage.py migrate
   ```

5. **Crea un superusuario:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecuta el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

7. **Accede a la aplicación:**
   - Abre tu navegador en `http://127.0.0.1:8000`
   - Panel de administración: `http://127.0.0.1:8000/admin`

## 📖 Uso

### Para Administradores
- **Dashboard**: Vista general con métricas y estadísticas
- **Productos**: Gestionar inventario y categorías
- **Clientes**: Administrar base de datos de clientes
- **Ventas**: Ver historial de ventas y tickets
- **Reportes**: Generar reportes de ventas y análisis

### Para Cajeros
- **Nueva Venta**: Interfaz simplificada para registrar ventas
- **Buscar Productos**: Búsqueda rápida en el inventario
- **Tickets**: Ver tickets de venta generados

## 🔧 Comandos Útiles

```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar pruebas
python manage.py test

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Verificar configuración
python manage.py check

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic
```

## 🎯 Funcionalidades Destacadas

### Búsqueda de Productos
- Búsqueda en tiempo real por nombre
- Filtros por categoría
- Interfaz intuitiva con resultados instantáneos

### Sistema de Roles
- **Administrador**: Acceso completo a todas las funciones
- **Cajero**: Acceso limitado a ventas y consulta de productos
- Navegación adaptada según el rol del usuario

### Dashboard Interactivo
- Gráficos de ventas por período
- Productos más vendidos
- Alertas de stock bajo
- Métricas financieras

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**NicoButter**
- 📧 Email: nicobutter@gmail.com
- 💼 LinkedIn: [\www.linkedin.com/in/nicolás-butterfield-9964aa1a3\]](https://www.linkedin.com/in/nicol%C3%A1s-butterfield-9964aa1a3/)
- 🐙 GitHub: [NicoButter](https://github.com/NicoButter)

## 🙏 Agradecimientos

## 🙏 Agradecimientos

- Django por el excelente framework web
- Chart.js por las visualizaciones
- Comunidad de Python y Django

---

⭐ Si este proyecto te resulta útil, ¡dale una estrella en GitHub!
