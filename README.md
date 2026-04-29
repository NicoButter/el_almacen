# 🏪 El Almacén

<div align="center">
  <img src="static/images/el_almacen_logo.png" alt="El Almacén Logo" width="200"/>
  
  *Sistema moderno de gestión de almacenes y ventas*
</div>

---

## ✨ Características Principales

### 👥 Gestión de Usuarios
- Sistema de autenticación con roles (Administrador, Cajero)
- Control de acceso basado en roles
- Navegación dinámica según permisos

### 📦 Gestión de Productos
- CRUD completo de productos
- Sistema de categorías
- Búsqueda avanzada de productos
- **Venta de productos fraccionados (por peso/kilo)**
- Control de stock en tiempo real
- Alertas de stock bajo

### 👥 Gestión de Clientes y Cuentas Corrientes
- Base de datos completa de clientes
- **Sistema de fiado / cuentas corrientes**
- Control del saldo de clientes y registro de abonos / pagos
- Historial de compras por cliente

### 💰 Sistema de Ventas
- Interfaz intuitiva y rápida para cajeros
- Venta con diferentes métodos de pago (Efectivo, Tarjeta, Débito, Fiado)
- Generación automática de tickets
- Validación de existencias y cálculos automáticos

### 📊 Dashboards y Reportes
- **Dashboard Administrativo**: Métricas clave del negocio, gráficos interactivos Chart.js, estado del inventario y alertas
- **Dashboard de Cajero**: Vista enfocada en turnos, ventas del día de acceso rápido
- **Reportes detallados**: Exportables y filtrables (Ventas por fecha, productos más vendidos, deudores)

### 🎨 Interfaz Moderna
- Diseño glassmorphism
- Interfaz responsive
- Tema oscuro con efectos visuales modernos
- Iconografía SVG personalizada

## 📸 Capturas de Pantalla

> **Nota**: Las capturas de pantalla deben colocarse en la carpeta `docs/screenshots/` (nombres sugeridos a continuación). ¡Sube las tuyas para lucir el proyecto!

### Dashboards (Administrador / Cajero)
<div align="center">
  <img src="docs/screenshots/dashboard-admin.png" alt="Dashboard Administrativo (Dashboard)" width="800"/>
  <p><em>Dashboard Administrador: Métricas, Gráficos Chart.js, y alertas en tiempo real</em></p>

  <img src="docs/screenshots/dashboard-cajero.png" alt="Dashboard Cajero (Dashboard)" width="800"/>
  <p><em>Dashboard Cajero: Ventas por turno y caja diaria</em></p>
</div>

### Punto de Venta (POS) y Cuentas Corrientes
<div align="center">
  <img src="docs/screenshots/nueva-venta.png" alt="Punto de Venta" width="800"/>
  <p><em>Interfaz rápida para registro de ventas, cálculo de fiado y métodos de pago</em></p>

  <img src="docs/screenshots/cuentas-corrientes.png" alt="Cuentas Corrientes y Fiado" width="800"/>
  <p><em>Gestión de pagos, abonos y control del saldo pendiente por cliente</em></p>
</div>

### Inventario y Reportes
<div align="center">
  <img src="docs/screenshots/lista-productos.png" alt="Gestión de Productos" width="800"/>
  <p><em>Lista de stock con soporte para fraccionado, alertas integradas e importación/exportación</em></p>

  <img src="docs/screenshots/reportes-estadisticas.png" alt="Reportes de Sistema" width="800"/>
  <p><em>Filtros detallados y estadísticas financieras</em></p>
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

**Nicolas Butterfield**
- 📧 Email: nicobutter@gmail.com
- 💼 LinkedIn: [Nicolás Butterfield](https://www.linkedin.com/in/nicol%C3%A1s-butterfield-9964aa1a3/)
- 🐙 GitHub: [nicobutter](https://github.com/nicobutter)

## 🙏 Agradecimientos

- Django por el excelente framework web
- Chart.js por las visualizaciones
- Comunidad de Python y Django

---

⭐ Si este proyecto te resulta útil, ¡dale una estrella en GitHub!
