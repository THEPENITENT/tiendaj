from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = 'tiendaj-secret-key-2026'


# ─────────────────────────────────────
# PÁGINA PRINCIPAL
# ─────────────────────────────────────
@app.route('/')
def index():
    conn = get_connection()
    if not conn:
        return render_template('error.html', msg='No se pudo conectar a la base de datos')

    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM videojuego')
    total_juegos = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as total FROM cliente')
    total_clientes = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as total FROM venta')
    total_ventas = cursor.fetchone()['total']

    cursor.execute('SELECT COALESCE(SUM(total), 0) as ingresos FROM venta')
    ingresos = cursor.fetchone()['ingresos']

    # Últimas 5 ventas
    cursor.execute('''
        SELECT v.id, c.nombre, c.apellido_paterno, v.total,
               v.metodo_pago, v.fecha_venta
        FROM venta v
        JOIN cliente c ON v.cliente_id = c.id
        ORDER BY v.fecha_venta DESC LIMIT 5
    ''')
    ultimas_ventas = cursor.fetchall()

    conn.close()

    return render_template('index.html',
                           total_juegos=total_juegos,
                           total_clientes=total_clientes,
                           total_ventas=total_ventas,
                           ingresos=ingresos,
                           ultimas_ventas=ultimas_ventas)


# ─────────────────────────────────────
# VIDEOJUEGOS
# ─────────────────────────────────────
@app.route('/videojuegos')
def videojuegos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, c.nombre as clasificacion, p.nombre as plataforma
        FROM videojuego v
        JOIN clasificacion c ON v.clasificacion_id = c.id
        JOIN plataforma p ON v.plataforma_id = p.id
        ORDER BY v.titulo
    ''')
    juegos = cursor.fetchall()

    cursor.execute('SELECT * FROM clasificacion ORDER BY nombre')
    clasificaciones = cursor.fetchall()

    cursor.execute('SELECT * FROM plataforma ORDER BY nombre')
    plataformas = cursor.fetchall()

    conn.close()
    return render_template('videojuegos.html',
                           juegos=juegos,
                           clasificaciones=clasificaciones,
                           plataformas=plataformas)


@app.route('/videojuegos/agregar', methods=['POST'])
def agregar_videojuego():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO videojuego (titulo, precio, clasificacion_id, plataforma_id,
                                    fecha_lanzamiento, stock)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            request.form['titulo'],
            request.form['precio'],
            request.form['clasificacion_id'],
            request.form['plataforma_id'],
            request.form['fecha_lanzamiento'] or None,
            request.form['stock']
        ))
        conn.commit()
        flash('Videojuego agregado correctamente', 'success')
    except Exception as e:
        flash(f'Error al agregar: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('videojuegos'))


@app.route('/videojuegos/eliminar/<int:id>')
def eliminar_videojuego(id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM videojuego WHERE id = %s', (id,))
        conn.commit()
        flash('Videojuego eliminado', 'success')
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('videojuegos'))


# ─────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────
@app.route('/clientes')
def clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cliente ORDER BY nombre')
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)


@app.route('/clientes/agregar', methods=['POST'])
def agregar_cliente():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO cliente (nombre, apellido_paterno, apellido_materno, email, telefono)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            request.form['nombre'],
            request.form['apellido_paterno'],
            request.form['apellido_materno'] or None,
            request.form['email'] or None,
            request.form['telefono'] or None
        ))
        conn.commit()
        flash('Cliente agregado correctamente', 'success')
    except Exception as e:
        flash(f'Error al agregar: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('clientes'))


@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM cliente WHERE id = %s', (id,))
        conn.commit()
        flash('Cliente eliminado', 'success')
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('clientes'))


# ─────────────────────────────────────
# VENTAS
# ─────────────────────────────────────
@app.route('/ventas')
def ventas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT v.*, c.nombre, c.apellido_paterno
        FROM venta v
        JOIN cliente c ON v.cliente_id = c.id
        ORDER BY v.fecha_venta DESC
    ''')
    ventas = cursor.fetchall()

    cursor.execute('SELECT id, nombre, apellido_paterno FROM cliente ORDER BY nombre')
    clientes = cursor.fetchall()

    cursor.execute('SELECT id, titulo, precio, stock FROM videojuego WHERE stock > 0 ORDER BY titulo')
    juegos = cursor.fetchall()

    conn.close()
    return render_template('ventas.html', ventas=ventas, clientes=clientes, juegos=juegos)


@app.route('/ventas/agregar', methods=['POST'])
def agregar_venta():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        videojuego_id = int(request.form['videojuego_id'])
        cantidad = int(request.form['cantidad'])

        # Obtener precio del videojuego
        cursor.execute('SELECT precio, stock FROM videojuego WHERE id = %s', (videojuego_id,))
        juego = cursor.fetchone()

        if not juego:
            flash('Videojuego no encontrado', 'error')
            return redirect(url_for('ventas'))

        if juego['stock'] < cantidad:
            flash(f'Stock insuficiente. Disponible: {juego["stock"]}', 'error')
            return redirect(url_for('ventas'))

        subtotal = juego['precio'] * cantidad

        # Crear venta
        cursor.execute('''
            INSERT INTO venta (cliente_id, total, metodo_pago)
            VALUES (%s, %s, %s)
        ''', (request.form['cliente_id'], subtotal, request.form['metodo_pago']))

        venta_id = cursor.lastrowid

        # Crear detalle
        cursor.execute('''
            INSERT INTO detalle_venta (venta_id, videojuego_id, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        ''', (venta_id, videojuego_id, cantidad, juego['precio'], subtotal))

        # Actualizar stock
        cursor.execute('UPDATE videojuego SET stock = stock - %s WHERE id = %s',
                        (cantidad, videojuego_id))

        conn.commit()
        flash(f'Venta registrada. Total: ${subtotal:,.2f}', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al registrar venta: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('ventas'))


# ─────────────────────────────────────
# INICIAR APP
# ─────────────────────────────────────
if __name__ == '__main__':
    print("Inicializando base de datos...")
    init_db()
    print("Servidor corriendo en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
