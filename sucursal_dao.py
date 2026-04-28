# sucursal_dao.py — Acceso a datos de sucursales
from conexion import obtener_conexion


class SucursalDAO:
    """
    sucursales → padre de inventarios, Ventas, telefono, Correos, empleados
    Padre directo: calle (FK calle_idcalle)
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
                "SELECT s.idsucursal, s.calle_idcalle, c.nombrecalle, "
                "s.nombre_sucursal, s.n_exterior, s.n_interior "
                "FROM sucursales s JOIN calle c ON s.calle_idcalle = c.idcalle "
                "ORDER BY s.idsucursal"
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

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idsucursal, calle_idcalle, nombre_sucursal, n_exterior, n_interior "
                "FROM sucursales WHERE idsucursal = ?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        """Sucursales tiene MUCHOS hijos: inventarios, Ventas, telefono, Correos, empleados."""
        con = self._con()
        try:
            cur = con.cursor()
            for tabla, col in [
                ("inventarios", "sucursales_idsucursal"),
                ("Ventas", "sucursales_idsucursal"),
                ("telefono", "sucursales_idsucursal"),
                ("Correos", "sucursales_idsucursal"),
                ("empleados", "sucursales_idsucursal"),
            ]:
                cur.execute(f"SELECT 1 FROM {tabla} WHERE {col} = ?", (id_,))
                if cur.fetchone():
                    return True
            return False
        finally:
            con.close()

    def insertar(self, id_calle, nombre, n_ext, n_int):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO sucursales (calle_idcalle, nombre_sucursal, n_exterior, n_interior) "
                "VALUES (?, ?, ?, ?)",
                (id_calle, nombre, n_ext, n_int or None))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_calle, nombre, n_ext, n_int):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE sucursales SET calle_idcalle=?, nombre_sucursal=?, "
                "n_exterior=?, n_interior=? WHERE idsucursal=?",
                (id_calle, nombre, n_ext, n_int or None, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM sucursales WHERE idsucursal=?", (id_,))
            con.commit()
        finally:
            con.close()
