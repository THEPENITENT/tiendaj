# plataforma_dao.py — Acceso a datos de Plataforma
from conexion import obtener_conexion


class PlataformaDAO:
    """
    Plataforma → padre de inventarios
    Padre directo: Videojuego (FK Videojuego_idVideojuego)
    """

    def _con(self):
        con = obtener_conexion()
        if con is None:
            raise Exception("No se pudo conectar a SQL Server.")
        return con

    def obtener_por_videojuego(self, id_vid):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idPlataforma, Videojuego_idVideojuego, Nombre "
                "FROM Plataforma WHERE Videojuego_idVideojuego = ? "
                "ORDER BY idPlataforma", (id_vid,))
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

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idPlataforma, Videojuego_idVideojuego, Nombre "
                "FROM Plataforma WHERE idPlataforma=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM inventarios WHERE Plataforma_idPlataforma=?", (id_,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_, id_vid, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Plataforma (idPlataforma, Videojuego_idVideojuego, Nombre) "
                "VALUES (?, ?, ?)", (id_, id_vid, nombre or None))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_vid, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE Plataforma SET Videojuego_idVideojuego=?, Nombre=? "
                "WHERE idPlataforma=?", (id_vid, nombre or None, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM Plataforma WHERE idPlataforma=?", (id_,))
            con.commit()
        finally:
            con.close()
