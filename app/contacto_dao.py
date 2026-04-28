# contacto_dao.py — DAOs de telefono y Correos
from conexion import obtener_conexion


def _con():
    con = obtener_conexion()
    if con is None:
        raise Exception("No se pudo conectar a SQL Server.")
    return con


# ═══════════════════════════════════════════════════════════════════════════════
class TelefonoDAO:
    """
    telefono → no tiene hijos
    Padres opcionales (4 FK, todas NULL): proveedores, empleados, sucursales, Clientes
    Solo se debe llenar UNO de los 4 campos por registro.
    """

    def obtener_todos(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idtelefono, numerotelefono, "
                "proveedores_id_proveedor, empleados_idempleados, "
                "sucursales_idsucursal, Clientes_idClientes "
                "FROM telefono ORDER BY idtelefono"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_por_filtro(self, tipo, id_padre):
        """tipo: 'proveedor' | 'empleado' | 'sucursal' | 'cliente'"""
        col = {
            "proveedor": "proveedores_id_proveedor",
            "empleado":  "empleados_idempleados",
            "sucursal":  "sucursales_idsucursal",
            "cliente":   "Clientes_idClientes",
        }[tipo]
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                f"SELECT idtelefono, numerotelefono FROM telefono "
                f"WHERE {col}=? ORDER BY idtelefono", (id_padre,))
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT idtelefono, numerotelefono, proveedores_id_proveedor, "
                "empleados_idempleados, sucursales_idsucursal, Clientes_idClientes "
                "FROM telefono WHERE idtelefono=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        return False

    def insertar(self, numero, id_prov, id_emp, id_suc, id_cli):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO telefono (numerotelefono, proveedores_id_proveedor, "
                "empleados_idempleados, sucursales_idsucursal, Clientes_idClientes) "
                "VALUES (?, ?, ?, ?, ?)",
                (numero, id_prov, id_emp, id_suc, id_cli))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, numero, id_prov, id_emp, id_suc, id_cli):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE telefono SET numerotelefono=?, proveedores_id_proveedor=?, "
                "empleados_idempleados=?, sucursales_idsucursal=?, Clientes_idClientes=? "
                "WHERE idtelefono=?",
                (numero, id_prov, id_emp, id_suc, id_cli, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM telefono WHERE idtelefono=?", (id_,))
            con.commit()
        finally:
            con.close()


# ═══════════════════════════════════════════════════════════════════════════════
class CorreoDAO:
    """
    Correos → no tiene hijos
    Padres opcionales (4 FK, todas NULL): Clientes, sucursales, empleados, proveedores
    """

    def obtener_todos(self):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id_correo, correo, Clientes_idClientes, "
                "sucursales_idsucursal, empleados_idempleados, proveedores_id_proveedor "
                "FROM Correos ORDER BY id_correo"
            )
            return cur.fetchall()
        finally:
            con.close()

    def obtener_por_filtro(self, tipo, id_padre):
        col = {
            "proveedor": "proveedores_id_proveedor",
            "empleado":  "empleados_idempleados",
            "sucursal":  "sucursales_idsucursal",
            "cliente":   "Clientes_idClientes",
        }[tipo]
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                f"SELECT id_correo, correo FROM Correos "
                f"WHERE {col}=? ORDER BY id_correo", (id_padre,))
            return cur.fetchall()
        finally:
            con.close()

    def buscar_por_id(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id_correo, correo, Clientes_idClientes, sucursales_idsucursal, "
                "empleados_idempleados, proveedores_id_proveedor FROM Correos WHERE id_correo=?", (id_,))
            return cur.fetchone()
        finally:
            con.close()

    def existe(self, id_):
        return self.buscar_por_id(id_) is not None

    def tiene_hijos(self, id_):
        return False

    def insertar(self, correo, id_cli, id_suc, id_emp, id_prov):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Correos (correo, Clientes_idClientes, sucursales_idsucursal, "
                "empleados_idempleados, proveedores_id_proveedor) VALUES (?, ?, ?, ?, ?)",
                (correo, id_cli, id_suc, id_emp, id_prov))
            con.commit()
        finally:
            con.close()

    def actualizar(self, id_, correo, id_cli, id_suc, id_emp, id_prov):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE Correos SET correo=?, Clientes_idClientes=?, sucursales_idsucursal=?, "
                "empleados_idempleados=?, proveedores_id_proveedor=? WHERE id_correo=?",
                (correo, id_cli, id_suc, id_emp, id_prov, id_))
            con.commit()
        finally:
            con.close()

    def eliminar(self, id_):
        con = _con()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM Correos WHERE id_correo=?", (id_,))
            con.commit()
        finally:
            con.close()
