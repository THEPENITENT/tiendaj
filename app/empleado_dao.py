# empleado_dao.py — Acceso a datos de empleados
from conexion import obtener_conexion


class EmpleadoDAO:
    """
    empleados → padre de telefono, Correos, Ventas
    Padres directos: calle, sucursales (DOS FK)
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
                "SELECT e.idempleados, e.sucursales_idsucursal, s.nombre_sucursal, "
                "e.calle_idcalle, c.nombrecalle, e.nombre_empleado, e.apellido_P, "
                "e.apellido_m, e.curp, e.rfc, e.puesto "
                "FROM empleados e "
                "JOIN sucursales s ON e.sucursales_idsucursal = s.idsucursal "
                "JOIN calle c ON e.calle_idcalle = c.idcalle "
                "ORDER BY e.idempleados"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_calles(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idcalle, nombrecalle FROM calle ORDER BY nombrecalle")
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

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idempleados, calle_idcalle, sucursales_idsucursal, "
                "nombre_empleado, apellido_P, apellido_m, curp, rfc, puesto, contrasena "
                "FROM empleados WHERE idempleados=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def curp_duplicado(self, curp, excluir_id=None):
        con = self._con()
        try:
            cur = con.cursor()
            if excluir_id:
                cur.execute("SELECT 1 FROM empleados WHERE curp=? AND idempleados<>?",
                            (curp, excluir_id))
            else:
                cur.execute("SELECT 1 FROM empleados WHERE curp=?", (curp,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def rfc_duplicado(self, rfc, excluir_id=None):
        con = self._con()
        try:
            cur = con.cursor()
            if excluir_id:
                cur.execute("SELECT 1 FROM empleados WHERE rfc=? AND idempleados<>?",
                            (rfc, excluir_id))
            else:
                cur.execute("SELECT 1 FROM empleados WHERE rfc=?", (rfc,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def tiene_hijos(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            for tabla, col in [
                ("Ventas",   "empleados_idempleados"),
                ("telefono", "empleados_idempleados"),
                ("Correos",  "empleados_idempleados"),
            ]:
                cur.execute(f"SELECT 1 FROM {tabla} WHERE {col}=?", (id_,))
                if cur.fetchone():
                    return True
            return False
        finally:
            con.close()

    def insertar(self, id_calle, id_suc, nombre, ap, am, curp, rfc, puesto, contrasena):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO empleados (calle_idcalle, sucursales_idsucursal, nombre_empleado, "
                "apellido_P, apellido_m, curp, rfc, puesto, contrasena) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (id_calle, id_suc, nombre, ap, am, curp, rfc, puesto, contrasena or None))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_calle, id_suc, nombre, ap, am, curp, rfc, puesto, contrasena):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE empleados SET calle_idcalle=?, sucursales_idsucursal=?, "
                "nombre_empleado=?, apellido_P=?, apellido_m=?, curp=?, rfc=?, "
                "puesto=?, contrasena=? WHERE idempleados=?",
                (id_calle, id_suc, nombre, ap, am, curp, rfc, puesto,
                 contrasena or None, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM empleados WHERE idempleados=?", (id_,))
            con.commit()
        finally:
            con.close()
