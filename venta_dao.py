# venta_dao.py — Acceso a datos de Ventas
from conexion import obtener_conexion


class VentaDAO:
    """
    Ventas → padre de Detalle_Ventas
    Padres directos: sucursales, empleados, Clientes (TRES FK)
    CHECK: MetodoPago IN ('Efectivo', 'Tarjeta', 'Transferencia')
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
                "SELECT v.idVentas, v.sucursales_idsucursal, s.nombre_sucursal, "
                "v.empleados_idempleados, e.nombre_empleado, "
                "v.Clientes_idClientes, c.Nombre, "
                "v.FechaVenta, v.Total, v.MetodoPago "
                "FROM Ventas v "
                "JOIN sucursales s ON v.sucursales_idsucursal = s.idsucursal "
                "JOIN empleados e ON v.empleados_idempleados = e.idempleados "
                "JOIN Clientes c ON v.Clientes_idClientes = c.idClientes "
                "ORDER BY v.idVentas DESC"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_sucursales(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idsucursal, nombre_sucursal FROM sucursales ORDER BY nombre_sucursal")
            return cur.fetchall()
        finally:
            con.close()

    def obtener_empleados(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idempleados, nombre_empleado FROM empleados ORDER BY nombre_empleado")
            return cur.fetchall()
        finally:
            con.close()

    def obtener_clientes(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idClientes, Nombre FROM Clientes ORDER BY Nombre")
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idVentas, sucursales_idsucursal, empleados_idempleados, "
                "Clientes_idClientes, FechaVenta, Total, MetodoPago "
                "FROM Ventas WHERE idVentas=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM Detalle_Ventas WHERE Ventas_idVentas=?", (id_,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_suc, id_emp, id_cli, fecha, total, metodo):
        """Inserta una venta. La fecha se pasa como parámetro desde Python
        (puede ser datetime.now() automático o una fecha manual del usuario)."""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Ventas (sucursales_idsucursal, empleados_idempleados, "
                "Clientes_idClientes, FechaVenta, Total, MetodoPago) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (id_suc, id_emp, id_cli, fecha, total, metodo))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_suc, id_emp, id_cli, fecha, total, metodo):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE Ventas SET sucursales_idsucursal=?, empleados_idempleados=?, "
                "Clientes_idClientes=?, FechaVenta=?, Total=?, MetodoPago=? WHERE idVentas=?",
                (id_suc, id_emp, id_cli, fecha, total, metodo, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM Ventas WHERE idVentas=?", (id_,))
            con.commit()
        finally:
            con.close()
