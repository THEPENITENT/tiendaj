from conexion import obtener_conexion


class ClasificacionDAO:
    """Todo el acceso a datos de la tabla clasificacion vive aquí."""

    def _con(self):
        con = obtener_conexion()
        if con is None:
            raise Exception("No se pudo conectar a SQL Server.")
        return con

    def obtener_todos(self):
        """Retorna lista de tuplas (idclasificacion, nombre_clasificacion)."""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idclasificacion, nombre_clasificacion "
                "FROM clasificacion ORDER BY idclasificacion"
            )
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        """Retorna la fila si existe, None si no."""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idclasificacion, nombre_clasificacion "
                "FROM clasificacion WHERE idclasificacion = ?", (id_,)
            )
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        """True si el ID ya está registrado en la tabla."""
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        """True si algún Videojuego referencia esta clasificación (no se puede eliminar)."""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT 1 FROM Videojuego "
                "WHERE clasificacion_idclasificacion = ?", (id_,)
            )
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO clasificacion (idclasificacion, nombre_clasificacion) "
                "VALUES (?, ?)", (id_, nombre)
            )
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE clasificacion SET nombre_clasificacion = ? "
                "WHERE idclasificacion = ?", (nombre, id_)
            )
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM clasificacion WHERE idclasificacion = ?", (id_,)
            )
            con.commit()
        finally:
            con.close()
