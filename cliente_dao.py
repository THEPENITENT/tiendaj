# cliente_dao.py — Acceso a datos de Clientes
from conexion import obtener_conexion


class ClienteDAO:
    """
    Clientes → padre de telefono, Correos, Ventas
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
                "SELECT cl.idClientes, cl.calle_idcalle, c.nombrecalle, "
                "cl.Nombre, cl.Apellido_Paterno, cl.Apellido_Materno, cl.FechaRegistro "
                "FROM Clientes cl JOIN calle c ON cl.calle_idcalle = c.idcalle "
                "ORDER BY cl.idClientes"
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
                "SELECT idClientes, calle_idcalle, Nombre, Apellido_Paterno, "
                "Apellido_Materno, FechaRegistro FROM Clientes WHERE idClientes=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            for tabla, col in [
                ("Ventas",   "Clientes_idClientes"),
                ("telefono", "Clientes_idClientes"),
                ("Correos",  "Clientes_idClientes"),
            ]:
                cur.execute(f"SELECT 1 FROM {tabla} WHERE {col} = ?", (id_,))
                if cur.fetchone():
                    return True
            return False
        finally:
            con.close()

    def insertar(self, id_calle, nombre, ap, am):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Clientes (calle_idcalle, Nombre, Apellido_Paterno, Apellido_Materno) "
                "VALUES (?, ?, ?, ?)",
                (id_calle, nombre or None, ap or None, am or None))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_calle, nombre, ap, am):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE Clientes SET calle_idcalle=?, Nombre=?, Apellido_Paterno=?, "
                "Apellido_Materno=? WHERE idClientes=?",
                (id_calle, nombre or None, ap or None, am or None, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM Clientes WHERE idClientes=?", (id_,))
            con.commit()
        finally:
            con.close()
