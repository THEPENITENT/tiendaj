# genero_dao.py — Acceso a datos de la tabla Genero (abuela, sin FK)
from conexion import obtener_conexion


class GeneroDAO:
    def _con(self):
        con = obtener_conexion()
        if con is None:
            raise Exception("No se pudo conectar a SQL Server.")
        return con

    def obtener_todos(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idGenero, NombreGenero FROM Genero ORDER BY idGenero")
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idGenero, NombreGenero FROM Genero WHERE idGenero = ?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        """Genero tiene hijos si hay videojuegos con ese género (tabla Genero_Videojuego si existe,
        de momento revisamos Videojuego directamente si tuviera la FK)."""
        # Por ahora la tabla Genero no tiene hijos directos en el esquema actual
        # Se dejará preparado para cuando se agregue Genero_Videojuego
        return False

    def insertar(self, id_, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO Genero (idGenero, NombreGenero) VALUES (?, ?)", (id_, nombre))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("UPDATE Genero SET NombreGenero = ? WHERE idGenero = ?", (nombre, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM Genero WHERE idGenero = ?", (id_,))
            con.commit()
        finally:
            con.close()
