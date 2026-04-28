# inventario_dao.py — Acceso a datos de inventarios
from conexion import obtener_conexion


class InventarioDAO:
    """
    inventarios → no tiene hijos
    Padres directos: Plataforma, sucursales (DOS FK)
    CHECK: stock >= 0
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
                "SELECT i.idinventario, i.Plataforma_idPlataforma, p.Nombre, "
                "i.sucursales_idsucursal, s.nombre_sucursal, i.nombre_inventario, i.stock "
                "FROM inventarios i "
                "JOIN Plataforma p ON i.Plataforma_idPlataforma = p.idPlataforma "
                "JOIN sucursales s ON i.sucursales_idsucursal = s.idsucursal "
                "ORDER BY i.idinventario"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_plataformas(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idPlataforma, Nombre FROM Plataforma ORDER BY Nombre")
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
                "SELECT idinventario, Plataforma_idPlataforma, sucursales_idsucursal, "
                "nombre_inventario, stock FROM inventarios WHERE idinventario=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        return False  # inventarios no tiene tablas hijas

    def insertar(self, id_plat, id_suc, nombre, stock):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO inventarios (Plataforma_idPlataforma, sucursales_idsucursal, "
                "nombre_inventario, stock) VALUES (?, ?, ?, ?)",
                (id_plat, id_suc, nombre or None, stock))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_plat, id_suc, nombre, stock):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE inventarios SET Plataforma_idPlataforma=?, sucursales_idsucursal=?, "
                "nombre_inventario=?, stock=? WHERE idinventario=?",
                (id_plat, id_suc, nombre or None, stock, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM inventarios WHERE idinventario=?", (id_,))
            con.commit()
        finally:
            con.close()
