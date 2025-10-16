# Arquitectura de Estilos del Dashboard

## 📋 Índice
1. [Introducción](#introducción)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Convención de Nombres](#convención-de-nombres)
4. [Jerarquía de Estilos](#jerarquía-de-estilos)
5. [Guía de Uso](#guía-de-uso)
6. [Ejemplos](#ejemplos)

---

## Introducción

Este documento define la arquitectura de estilos CSS del dashboard para **prevenir conflictos** entre los estilos base del dashboard y los estilos de las páginas individuales.

### Principios Fundamentales

1. **Separación clara**: Los estilos base nunca deben ser modificados por páginas individuales
2. **Prefijos consistentes**: Cada nivel tiene su propio prefijo de clase
3. **Scope específico**: Los estilos de página solo afectan al contenido de la página
4. **Sin global overrides**: Ninguna página puede redefinir variables o clases globales

---

## Estructura de Archivos

```
static/
└── css/
    ├── base_dashboard.css      # Estilos base del dashboard (NO MODIFICAR)
    └── bootstrap.min.css       # Framework CSS

products/
└── static/
    └── products/
        └── css/
            └── list_products_page.css  # Estilos específicos de productos

reports/
└── static/
    └── reports/
        └── css/
            └── reports_page.css        # Estilos específicos de reportes
```

---

## Convención de Nombres

### Prefijo `base-` - Estilos del Dashboard Base

**USO**: Estructura principal del dashboard (sidebar, contenedor, navegación)

**UBICACIÓN**: `/static/css/base_dashboard.css`

**EJEMPLOS**:
- `.base-dashboard-container`
- `.base-sidebar`
- `.base-sidebar-nav`
- `.base-sidebar-link`
- `.base-content-area`
- `.base-page-title`

**REGLA**: ❌ **NUNCA** redefinir estas clases en archivos de página

---

### Prefijo `page-` - Estilos de Página Específicos

**USO**: Contenido específico de cada página individual

**UBICACIÓN**: `/[app]/static/[app]/css/[page]_page.css`

**EJEMPLOS**:
- `.page-products-container`
- `.page-metrics-section`
- `.page-table`
- `.page-chart-card`

**REGLA**: ✅ Usar solo dentro del bloque `{% block page_content %}`

---

### Variables CSS

#### Variables Globales (`--base-*`)

Definidas en `base_dashboard.css`:

```css
:root {
    --base-background: #020617;
    --base-foreground: #f8fafc;
    --base-card: rgba(15,23,42,0.7);
    --base-primary: #7f3cff;
    --base-accent: #6ee7b7;
    --base-border: rgba(148,163,184,0.2);
    --base-radius: 12px;
}
```

**REGLA**: ❌ **NUNCA** redefinir estas variables en archivos de página

**USO EN PÁGINAS**: ✅ Puedes **usar** estas variables, pero NO redefinirlas

```css
/* ✅ CORRECTO */
.page-card {
    background: var(--base-card);
    border: 1px solid var(--base-border);
}

/* ❌ INCORRECTO */
:root {
    --base-card: red; /* NO redefinir variables globales */
}
```

---

## Jerarquía de Estilos

```
┌─────────────────────────────────────────────┐
│ base.html (Dashboard Base Structure)       │
│ - base-dashboard-container                  │
│ - base-sidebar                              │
│ - base-content-area                         │
│   └─ page-wrapper                           │
│       └─ {% block page_content %}           │
│           ┌─────────────────────────────┐   │
│           │ Página Individual           │   │
│           │ (ej: list_products.html)    │   │
│           │                             │   │
│           │ .page-products-container    │   │
│           │   .page-metrics-section     │   │
│           │   .page-table               │   │
│           │   .page-chart-card          │   │
│           └─────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## Guía de Uso

### Para `base.html`

```django
<!DOCTYPE html>
<html lang="es">
<head>
    <!-- BASE STYLES: Estilos globales del dashboard -->
    <link href="{% static 'css/base_dashboard.css' %}" rel="stylesheet">
    
    <!-- PAGE STYLES: Estilos específicos de cada página -->
    {% block extra_styles %}{% endblock %}
</head>
<body class="base-dashboard">
    <div class="base-dashboard-container">
        <aside class="base-sidebar">
            <!-- Sidebar content -->
        </aside>
        <main class="base-content-area">
            <div class="page-wrapper">
                {% block page_content %}
                <!-- Contenido de página se inyecta aquí -->
                {% endblock %}
            </div>
        </main>
    </div>
</body>
</html>
```

### Para Páginas Individuales

```django
{% extends 'base.html' %}
{% load static %}

{% block extra_styles %}
    <link href="{% static 'products/css/list_products_page.css' %}" rel="stylesheet">
{% endblock %}

{% block body_class %}page-products{% endblock %}

{% block page_content %}
<div class="page-products-container">
    <h1 class="base-page-title">Gestión de Productos</h1>
    
    <section class="page-metrics-section">
        <!-- Métricas -->
    </section>
    
    <div class="page-table-container">
        <table class="page-table">
            <!-- Tabla de productos -->
        </table>
    </div>
</div>
{% endblock %}
```

---

## Ejemplos

### ✅ Ejemplo CORRECTO - Productos

**products/templates/products/list_products.html**
```django
{% block page_content %}
<div class="page-products-container">
    <h1 class="base-page-title">Productos</h1>
    
    <div class="page-metric-card">
        <div class="page-metric-value">150</div>
    </div>
    
    <table class="page-table">
        <!-- Tabla -->
    </table>
</div>
{% endblock %}
```

**products/static/products/css/list_products_page.css**
```css
.page-products-container {
    width: 100%;
}

.page-metric-card {
    background: var(--base-card);  /* ✅ Usar variables globales */
    padding: 20px;
}

.page-table {
    width: 100%;
    background: var(--base-card);
}
```

---

### ❌ Ejemplo INCORRECTO

```css
/* ❌ NO HACER ESTO */

/* Redefinir variables globales */
:root {
    --base-primary: red;
}

/* Modificar clases base */
.base-sidebar {
    background: blue;
}

/* Usar selectores genéricos sin prefijo */
.container {
    margin: 0;  /* Puede afectar al dashboard base */
}

h1 {
    color: green;  /* Afecta a todos los h1 del dashboard */
}

.btn {
    padding: 10px;  /* Clase genérica sin prefijo */
}
```

---

## Checklist para Nuevas Páginas

Al crear una nueva página, asegúrate de:

- [ ] ✅ Extender `base.html`
- [ ] ✅ Crear archivo CSS con nombre `[page]_page.css`
- [ ] ✅ Usar prefijo `page-` para todas las clases
- [ ] ✅ Usar variables `--base-*` sin redefinirlas
- [ ] ✅ Envolver contenido en contenedor con prefijo `page-`
- [ ] ✅ NO usar selectores genéricos (h1, p, div, etc.)
- [ ] ✅ NO modificar clases con prefijo `base-`
- [ ] ✅ NO redefinir variables globales

---

## Beneficios de Esta Arquitectura

1. **Sin conflictos de estilos**: Los prefijos garantizan aislamiento
2. **Mantenimiento fácil**: Cambios en una página no afectan otras
3. **Escalabilidad**: Puedes agregar páginas sin preocuparte por conflictos
4. **Debugging simple**: Sabes exactamente dónde están definidos los estilos
5. **Consistencia visual**: Variables globales mantienen diseño coherente

---

## Preguntas Frecuentes

### ¿Puedo usar Bootstrap en mis páginas?

✅ Sí, pero con cuidado. Usa clases específicas de Bootstrap y evita que sobrescriban estilos base.

### ¿Puedo compartir estilos entre páginas?

✅ Sí, crea un archivo `shared_page_components.css` con prefijo `page-` para componentes reutilizables.

### ¿Qué hago si necesito cambiar un estilo base?

⚠️ Edita SOLO `base_dashboard.css` y prueba que no rompa otras páginas.

### ¿Puedo usar clases de utilidad sin prefijo?

❌ No. Siempre usa prefijo `page-` para evitar conflictos.

---

## Contacto y Soporte

Para dudas sobre esta arquitectura, consulta este documento o contacta al equipo de desarrollo.

**Última actualización**: Octubre 2025
