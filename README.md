# Sistema de Inventario v1.0
### Aplicación Flask – CRUD básico de Productos y Ventas

---

## Requisitos

- Python 3.8 o superior
- pip

---

## Instalación

```bash
# 1. Clonar / descomprimir el proyecto
cd inventario

# 2. (Opcional) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install flask
```

---

## Poblar la base de datos (50 registros)

```bash
# El archivo inventario.db se crea automáticamente al primer arranque.
# Luego ejecutar el script de seed:

sqlite3 inventario.db < seed.sql
```

> En Windows sin sqlite3 en el PATH, puede usar [DB Browser for SQLite](https://sqlitebrowser.org/)
> y ejecutar el contenido de `seed.sql` desde la pestaña "Execute SQL".

---

## Ejecución

```bash
python app.py
```

Abrir el navegador en: **http://127.0.0.1:5000**

---

## Estructura del proyecto

```
inventario/
├── app.py                  # Aplicación principal (Flask + SQLite)
├── seed.sql                # 50 productos + 50 ventas de ejemplo
├── inventario.db           # Base de datos (se crea al primer arranque)
├── README.md
└── templates/
    ├── base.html
    ├── productos/
    │   ├── lista.html
    │   └── form.html
    └── ventas/
        ├── lista.html
        └── form.html
```

---

## Funcionalidades

| Módulo    | Crear | Leer | Editar | Eliminar |
|-----------|:-----:|:----:|:------:|:--------:|
| Productos |  ✔    |  ✔   |   ✔    |    ✔     |
| Ventas    |  ✔    |  ✔   |   ✔    |    ✔     |

- Al registrar una venta se descuenta el stock del producto.
- Al eliminar o editar una venta el stock se revierte automáticamente.
- Stock < 5 unidades se resalta en rojo en la tabla de productos.

---

## Limitaciones conocidas (intencionales)

- Sin paginación: todas las filas se muestran en una sola tabla.
- Sin filtros ni búsqueda.
- Sin reportes, gráficas ni indicadores.
- Sin autenticación de usuarios.
- Sin relaciones FK explícitas entre tablas.
- Base de datos de archivo local (SQLite); no apta para múltiples usuarios simultáneos.
