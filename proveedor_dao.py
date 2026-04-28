# proveedor_dao.py — Acceso a datos de la tabla proveedores (abuela, sin FK)
from conexion import obtener_conexion


class ProveedorDAO:
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
                "SELECT id_proveedor, nombre, rfc, apellido_paterno, apellido_materno "
                "FROM proveedores ORDER BY id_proveedor"
            )
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id_proveedor, nombre, rfc, apellido_paterno, apellido_materno "
                "FROM proveedores WHERE id_proveedor = ?", (id_,)
            )
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def rfc_duplicado(self, rfc, excluir_id=None):
        """Verifica que el RFC no esté ya registrado (es UNIQUE en la tabla)."""
        con = self._con()
        try:
            cur = con.cursor()
            if excluir_id:
                cur.execute(
                    "SELECT 1 FROM proveedores WHERE rfc = ? AND id_proveedor <> ?",
                    (rfc, excluir_id))
            else:
                cur.execute("SELECT 1 FROM proveedores WHERE rfc = ?", (rfc,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def tiene_hijos(self, id_):
        """Proveedor tiene hijos en telefono y Correos."""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM telefono WHERE proveedores_id_proveedor = ?", (id_,))
            if cur.fetchone():
                return True
            cur.execute("SELECT 1 FROM Correos WHERE proveedores_id_proveedor = ?", (id_,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, nombre, rfc, ap_paterno, ap_materno):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO proveedores (nombre, rfc, apellido_paterno, apellido_materno) "
                "VALUES (?, ?, ?, ?)",
                (nombre, rfc or None, ap_paterno or None, ap_materno or None)
            )
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, nombre, rfc, ap_paterno, ap_materno):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE proveedores SET nombre=?, rfc=?, apellido_paterno=?, apellido_materno=? "
                "WHERE id_proveedor=?",
                (nombre, rfc or None, ap_paterno or None, ap_materno or None, id_)
            )
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM proveedores WHERE id_proveedor = ?", (id_,))
            con.commit()
        finally:
            con.close()
