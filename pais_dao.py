# pais_dao.py — Acceso a datos de la tabla pais (abuela, sin FK)
from conexion import obtener_conexion


class PaisDAO:
    def _con(self):
        con = obtener_conexion()
        if con is None:
            raise Exception("No se pudo conectar a SQL Server.")
        return con

    def obtener_todos(self):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idpais, nombre_pais FROM pais ORDER BY idpais")
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idpais, nombre_pais FROM pais WHERE idpais = ?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        """Un país tiene hijos si tiene estados asociados."""
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM estados WHERE pais_idpais = ?", (id_,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO pais (idpais, nombre_pais) VALUES (?, ?)", (id_, nombre))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, nombre):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("UPDATE pais SET nombre_pais = ? WHERE idpais = ?", (nombre, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = self._con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM pais WHERE idpais = ?", (id_,))
            con.commit()
        finally:
            con.close()
