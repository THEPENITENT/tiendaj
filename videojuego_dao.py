# videojuego_dao.py — Acceso a datos de la tabla Videojuego
from conexion import obtener_conexion


class VideojuegoDAO:
    def _con(self):
        con = obtener_conexion()
        if con is None:
            raise Exception("No se pudo conectar a SQL Server.")
        return con

    def obtener_por_clasificacion(self, id_clas):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idVideojuego, Titulo, Precio, FechaLanzamiento "
                "FROM Videojuego WHERE clasificacion_idclasificacion = ? "
                "ORDER BY Titulo", (id_clas,)
            )
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_vid):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idVideojuego, clasificacion_idclasificacion, Titulo, Precio, FechaLanzamiento "
                "FROM Videojuego WHERE idVideojuego = ?", (id_vid,)
            )
            return cur.fetchone()
        finally:
            con.close()

    def tiene_hijos(self, id_vid):
        """No borrar si el juego tiene plataformas o está en ventas."""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM Plataforma WHERE Videojuego_idVideojuego = ?", (id_vid,))
            if cur.fetchone(): return True
            cur.execute("SELECT 1 FROM Detalle_Ventas WHERE Videojuego_idVideojuego = ?", (id_vid,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_clas, titulo, precio, fecha):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Videojuego (clasificacion_idclasificacion, Titulo, Precio, FechaLanzamiento) "
                "VALUES (?, ?, ?, ?)",
                (id_clas, titulo, precio, fecha)
            )
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_vid, titulo, precio, fecha):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE Videojuego SET Titulo=?, Precio=?, FechaLanzamiento=? "
                "WHERE idVideojuego=?",
                (titulo, precio, fecha, id_vid)
            )
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_vid):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM Videojuego WHERE idVideojuego = ?", (id_vid,))
            con.commit()
        finally:
            con.close()
