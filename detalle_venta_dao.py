# detalle_venta_dao.py — Acceso a datos de Detalle_Ventas
from conexion import obtener_conexion


class DetalleVentaDAO:
    """
    Detalle_Ventas → no tiene hijos
    Padres directos: Ventas, Videojuego, inventarios (TRES FK)
    CHECK: Cantidad > 0
    """

    def _con(self):
        con = obtener_conexion()
        if con is None:
            raise Exception("No se pudo conectar a SQL Server.")
        return con

    def obtener_todos(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT d.idDetalle, d.Ventas_idVentas, d.Videojuego_idVideojuego, v.Titulo, "
                "d.inventarios_idinventario, i.nombre_inventario, "
                "d.Cantidad, d.Precio_unitario, d.Subtotal "
                "FROM Detalle_Ventas d "
                "JOIN Videojuego  v ON d.Videojuego_idVideojuego = v.idVideojuego "
                "JOIN inventarios i ON d.inventarios_idinventario = i.idinventario "
                "ORDER BY d.idDetalle DESC"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_por_venta(self, id_venta):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT d.idDetalle, d.Ventas_idVentas, d.Videojuego_idVideojuego, v.Titulo, "
                "d.inventarios_idinventario, i.nombre_inventario, "
                "d.Cantidad, d.Precio_unitario, d.Subtotal "
                "FROM Detalle_Ventas d "
                "JOIN Videojuego  v ON d.Videojuego_idVideojuego = v.idVideojuego "
                "JOIN inventarios i ON d.inventarios_idinventario = i.idinventario "
                "WHERE d.Ventas_idVentas=? "
                "ORDER BY d.idDetalle", (id_venta,))
            return cur.fetchall()
        finally:
            con.close()

    def obtener_por_videojuego(self, id_vid):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT d.idDetalle, d.Ventas_idVentas, d.Videojuego_idVideojuego, v.Titulo, "
                "d.inventarios_idinventario, i.nombre_inventario, "
                "d.Cantidad, d.Precio_unitario, d.Subtotal "
                "FROM Detalle_Ventas d "
                "JOIN Videojuego  v ON d.Videojuego_idVideojuego = v.idVideojuego "
                "JOIN inventarios i ON d.inventarios_idinventario = i.idinventario "
                "WHERE d.Videojuego_idVideojuego=? "
                "ORDER BY d.idDetalle", (id_vid,))
            return cur.fetchall()
        finally:
            con.close()

    def obtener_ventas(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idVentas, FechaVenta FROM Ventas ORDER BY idVentas DESC")
            return cur.fetchall()
        finally:
            con.close()

    def obtener_videojuegos(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idVideojuego, Titulo FROM Videojuego ORDER BY Titulo")
            return cur.fetchall()
        finally:
            con.close()

    def obtener_inventarios(self):
        """Lista de inventarios con info útil:
        idinventario - nombre_inventario (sucursal / plataforma)  [stock]"""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT i.idinventario, i.nombre_inventario, "
                "s.nombre_sucursal, p.Nombre, i.stock "
                "FROM inventarios i "
                "JOIN sucursales s ON i.sucursales_idsucursal = s.idsucursal "
                "JOIN Plataforma  p ON i.Plataforma_idPlataforma = p.idPlataforma "
                "WHERE i.stock > 0 "
                "ORDER BY i.idinventario"
            )
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idDetalle, Ventas_idVentas, Videojuego_idVideojuego, "
                "inventarios_idinventario, Cantidad, Precio_unitario, Subtotal "
                "FROM Detalle_Ventas WHERE idDetalle=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        return False

    def insertar(self, id_venta, id_vid, id_inv, cantidad, precio):
        subtotal = cantidad * precio
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Detalle_Ventas (Ventas_idVentas, Videojuego_idVideojuego, "
                "inventarios_idinventario, Cantidad, Precio_unitario, Subtotal) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (id_venta, id_vid, id_inv, cantidad, precio, subtotal))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_venta, id_vid, id_inv, cantidad, precio):
        subtotal = cantidad * precio
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE Detalle_Ventas SET Ventas_idVentas=?, Videojuego_idVideojuego=?, "
                "inventarios_idinventario=?, Cantidad=?, Precio_unitario=?, Subtotal=? "
                "WHERE idDetalle=?",
                (id_venta, id_vid, id_inv, cantidad, precio, subtotal, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM Detalle_Ventas WHERE idDetalle=?", (id_,))
            con.commit()
        finally:
            con.close()
