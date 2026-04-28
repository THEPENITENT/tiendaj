# geo_dao.py — DAOs de la cadena geográfica: estados, ciudad, colonia, calle
from conexion import obtener_conexion


def _con():
    con = obtener_conexion()
    if con is None:
        raise Exception("No se pudo conectar a SQL Server.")
    return con


# ═══════════════════════════════════════════════════════════════════════════════
class EstadosDAO:
    """
    estados → hijo de pais
    - idestados:     VARCHAR(6)  PK
    - pais_idpais:   VARCHAR(6)  FK → pais
    - estadosnombre: VARCHAR(50) NOT NULL
    """

    def obtener_todos(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT e.idestados, e.pais_idpais, p.nombre_pais, e.estadosnombre "
                "FROM estados e JOIN pais p ON e.pais_idpais = p.idpais "
                "ORDER BY e.pais_idpais, e.idestados"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_paises(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idpais, nombre_pais FROM pais ORDER BY idpais")
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idestados, pais_idpais, estadosnombre FROM estados WHERE idestados = ?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM ciudad WHERE estados_idestados = ?", (id_,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_, id_pais, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO estados (idestados, pais_idpais, estadosnombre) VALUES (?,?,?)",
                (id_, id_pais, nombre))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_pais, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE estados SET pais_idpais=?, estadosnombre=? WHERE idestados=?",
                (id_pais, nombre, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM estados WHERE idestados=?", (id_,))
            con.commit()
        finally:
            con.close()


# ═══════════════════════════════════════════════════════════════════════════════
class CiudadDAO:
    """
    ciudad → hijo de estados
    - idciudad:          INT IDENTITY  PK
    - estados_idestados: VARCHAR(6)    FK → estados
    - nombre_ciudad:     VARCHAR(50)   NOT NULL
    """

    def obtener_todos(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT c.idciudad, c.estados_idestados, e.estadosnombre, c.nombre_ciudad "
                "FROM ciudad c JOIN estados e ON c.estados_idestados = e.idestados "
                "ORDER BY c.estados_idestados, c.nombre_ciudad"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_estados(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idestados, estadosnombre FROM estados ORDER BY idestados")
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idciudad, estados_idestados, nombre_ciudad FROM ciudad WHERE idciudad=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM colonia WHERE ciudad_idciudad=?", (id_,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_estado, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO ciudad (estados_idestados, nombre_ciudad) VALUES (?,?)",
                (id_estado, nombre))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_estado, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE ciudad SET estados_idestados=?, nombre_ciudad=? WHERE idciudad=?",
                (id_estado, nombre, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM ciudad WHERE idciudad=?", (id_,))
            con.commit()
        finally:
            con.close()


# ═══════════════════════════════════════════════════════════════════════════════
class ColoniaDAO:
    """
    colonia → hijo de ciudad
    - idcolonia:       VARCHAR(10) PK
    - ciudad_idciudad: INT         FK → ciudad
    - nombrecolonia:   VARCHAR(50) NOT NULL
    """

    def obtener_todos(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT col.idcolonia, col.ciudad_idciudad, c.nombre_ciudad, col.nombrecolonia "
                "FROM colonia col JOIN ciudad c ON col.ciudad_idciudad = c.idciudad "
                "ORDER BY col.ciudad_idciudad, col.idcolonia"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_ciudades(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idciudad, nombre_ciudad FROM ciudad ORDER BY nombre_ciudad")
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idcolonia, ciudad_idciudad, nombrecolonia FROM colonia WHERE idcolonia=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM calle WHERE colonia_idcolonia=?", (id_,))
            return cur.fetchone() is not None
        finally:
            con.close()

    def insertar(self, id_, id_ciudad, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO colonia (idcolonia, ciudad_idciudad, nombrecolonia) VALUES (?,?,?)",
                (id_, id_ciudad, nombre))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_ciudad, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE colonia SET ciudad_idciudad=?, nombrecolonia=? WHERE idcolonia=?",
                (id_ciudad, nombre, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM colonia WHERE idcolonia=?", (id_,))
            con.commit()
        finally:
            con.close()


# ═══════════════════════════════════════════════════════════════════════════════
class CalleDAO:
    """
    calle → hijo de colonia
    - idcalle:           INT IDENTITY  PK
    - colonia_idcolonia: VARCHAR(10)   FK → colonia
    - nombrecalle:       VARCHAR(100)  NOT NULL
    """

    def obtener_todos(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT ca.idcalle, ca.colonia_idcolonia, col.nombrecolonia, ca.nombrecalle "
                "FROM calle ca JOIN colonia col ON ca.colonia_idcolonia = col.idcolonia "
                "ORDER BY ca.colonia_idcolonia, ca.nombrecalle"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_colonias(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("SELECT idcolonia, nombrecolonia FROM colonia ORDER BY nombrecolonia")
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idcalle, colonia_idcolonia, nombrecalle FROM calle WHERE idcalle=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        """Calle es el fin de la cadena geográfica, pero puede estar en sucursales, clientes, empleados."""
        con = _con()
        try:
            cur = con.cursor()
            for tabla in ["sucursales", "Clientes", "empleados"]:
                cur.execute(f"SELECT 1 FROM {tabla} WHERE calle_idcalle=?", (id_,))
                if cur.fetchone(): return True
            return False
        finally:
            con.close()

    def insertar(self, id_colonia, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO calle (colonia_idcolonia, nombrecalle) VALUES (?,?)",
                (id_colonia, nombre))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, id_colonia, nombre):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE calle SET colonia_idcolonia=?, nombrecalle=? WHERE idcalle=?",
                (id_colonia, nombre, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM calle WHERE idcalle=?", (id_,))
            con.commit()
        finally:
            con.close()
