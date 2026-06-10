from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_123"
DB_PATH = "inventario.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            categoria   TEXT,
            precio      REAL NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0,
            proveedor   TEXT,
            codigo      TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id     INTEGER,
            producto_nombre TEXT,
            cantidad        INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            total           REAL NOT NULL,
            fecha           TEXT DEFAULT (date('now')),
            vendedor        TEXT
        );
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  PRODUCTOS – CRUD
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("listar_productos"))


@app.route("/productos")
def listar_productos():
    conn = get_db()
    productos = conn.execute("SELECT * FROM productos ORDER BY id").fetchall()
    conn.close()
    return render_template("productos/lista.html", productos=productos)


@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        datos = (
            request.form["nombre"],
            request.form["categoria"],
            float(request.form["precio"]),
            int(request.form["stock"]),
            request.form["proveedor"],
            request.form["codigo"],
        )
        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO productos (nombre,categoria,precio,stock,proveedor,codigo) VALUES (?,?,?,?,?,?)",
                datos,
            )
            conn.commit()
            conn.close()
            flash("Producto creado.", "success")
            return redirect(url_for("listar_productos"))
        except sqlite3.IntegrityError:
            flash("El código de producto ya existe.", "danger")
    return render_template("productos/form.html", producto=None)


@app.route("/productos/editar/<int:pid>", methods=["GET", "POST"])
def editar_producto(pid):
    conn = get_db()
    producto = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
    if not producto:
        conn.close()
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("listar_productos"))

    if request.method == "POST":
        datos = (
            request.form["nombre"],
            request.form["categoria"],
            float(request.form["precio"]),
            int(request.form["stock"]),
            request.form["proveedor"],
            request.form["codigo"],
            pid,
        )
        conn.execute(
            "UPDATE productos SET nombre=?,categoria=?,precio=?,stock=?,proveedor=?,codigo=? WHERE id=?",
            datos,
        )
        conn.commit()
        conn.close()
        flash("Producto actualizado.", "success")
        return redirect(url_for("listar_productos"))

    conn.close()
    return render_template("productos/form.html", producto=producto)


@app.route("/productos/eliminar/<int:pid>", methods=["POST"])
def eliminar_producto(pid):
    conn = get_db()
    conn.execute("DELETE FROM productos WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    flash("Producto eliminado.", "warning")
    return redirect(url_for("listar_productos"))


# ─────────────────────────────────────────────
#  VENTAS – CRUD
# ─────────────────────────────────────────────

@app.route("/ventas")
def listar_ventas():
    conn = get_db()
    ventas = conn.execute("SELECT * FROM ventas ORDER BY id").fetchall()
    conn.close()
    return render_template("ventas/lista.html", ventas=ventas)


@app.route("/ventas/nueva", methods=["GET", "POST"])
def nueva_venta():
    conn = get_db()
    productos = conn.execute("SELECT * FROM productos ORDER BY nombre").fetchall()

    if request.method == "POST":
        pid       = int(request.form["producto_id"])
        cantidad  = int(request.form["cantidad"])
        vendedor  = request.form["vendedor"]

        producto = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()
        if not producto:
            flash("Producto no encontrado.", "danger")
        elif producto["stock"] < cantidad:
            flash(f"Stock insuficiente. Disponible: {producto['stock']}.", "danger")
        else:
            total = round(producto["precio"] * cantidad, 2)
            conn.execute(
                "INSERT INTO ventas (producto_id,producto_nombre,cantidad,precio_unitario,total,vendedor) VALUES (?,?,?,?,?,?)",
                (pid, producto["nombre"], cantidad, producto["precio"], total, vendedor),
            )
            conn.execute(
                "UPDATE productos SET stock = stock - ? WHERE id=?", (cantidad, pid)
            )
            conn.commit()
            flash("Venta registrada.", "success")
            conn.close()
            return redirect(url_for("listar_ventas"))

    conn.close()
    return render_template("ventas/form.html", productos=productos, venta=None)


@app.route("/ventas/editar/<int:vid>", methods=["GET", "POST"])
def editar_venta(vid):
    conn = get_db()
    venta    = conn.execute("SELECT * FROM ventas WHERE id=?", (vid,)).fetchone()
    productos = conn.execute("SELECT * FROM productos ORDER BY nombre").fetchall()

    if not venta:
        conn.close()
        flash("Venta no encontrada.", "danger")
        return redirect(url_for("listar_ventas"))

    if request.method == "POST":
        pid      = int(request.form["producto_id"])
        cantidad = int(request.form["cantidad"])
        vendedor = request.form["vendedor"]
        producto = conn.execute("SELECT * FROM productos WHERE id=?", (pid,)).fetchone()

        if not producto:
            flash("Producto no encontrado.", "danger")
        else:
            # Revertir stock anterior y aplicar nuevo
            conn.execute(
                "UPDATE productos SET stock = stock + ? WHERE id=?",
                (venta["cantidad"], venta["producto_id"]),
            )
            total = round(producto["precio"] * cantidad, 2)
            conn.execute(
                "UPDATE ventas SET producto_id=?,producto_nombre=?,cantidad=?,precio_unitario=?,total=?,vendedor=? WHERE id=?",
                (pid, producto["nombre"], cantidad, producto["precio"], total, vendedor, vid),
            )
            conn.execute(
                "UPDATE productos SET stock = stock - ? WHERE id=?", (cantidad, pid)
            )
            conn.commit()
            conn.close()
            flash("Venta actualizada.", "success")
            return redirect(url_for("listar_ventas"))

    conn.close()
    return render_template("ventas/form.html", productos=productos, venta=venta)


@app.route("/ventas/eliminar/<int:vid>", methods=["POST"])
def eliminar_venta(vid):
    conn = get_db()
    venta = conn.execute("SELECT * FROM ventas WHERE id=?", (vid,)).fetchone()
    if venta:
        conn.execute(
            "UPDATE productos SET stock = stock + ? WHERE id=?",
            (venta["cantidad"], venta["producto_id"]),
        )
        conn.execute("DELETE FROM ventas WHERE id=?", (vid,))
        conn.commit()
    conn.close()
    flash("Venta eliminada.", "warning")
    return redirect(url_for("listar_ventas"))


@app.context_processor
def inject_now():
    from datetime import datetime
    return {"now": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
