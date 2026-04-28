-- ============================================
-- TIENDAJ - Schema de Base de Datos
-- Tienda de Videojuegos - Sistema MRP
-- ============================================

-- Crear la base de datos
-- CREATE DATABASE TIENDAjp;
-- GO
-- USE TIENDAjp;
-- GO

-- 1. Tablas Base (Independientes)
CREATE TABLE pais (
    idpais      VARCHAR(6)  NOT NULL,
    nombre_pais VARCHAR(50) NOT NULL,
    CONSTRAINT pk_pais PRIMARY KEY (idpais)
);

CREATE TABLE clasificacion (
    idclasificacion      VARCHAR(5)  NOT NULL,
    nombre_clasificacion VARCHAR(50) NULL,
    CONSTRAINT pk_clasificacion PRIMARY KEY (idclasificacion)
);

CREATE TABLE Genero (
    idGenero      VARCHAR(5)  NOT NULL,
    NombreGenero VARCHAR(50) NULL,
    CONSTRAINT pk_Genero PRIMARY KEY (idGenero)
);

CREATE TABLE proveedores (
    id_proveedor     INT          NOT NULL IDENTITY(1,1),
    nombre           VARCHAR(100) NOT NULL,
    rfc              VARCHAR(13)  UNIQUE NULL,
    apellido_paterno VARCHAR(50)  NULL,
    apellido_materno VARCHAR(50)  NULL,
    CONSTRAINT pk_proveedores PRIMARY KEY (id_proveedor)
);

-- 2. Tablas Geográficas
CREATE TABLE estados (
    idestados     VARCHAR(6)  NOT NULL,
    pais_idpais   VARCHAR(6)  NOT NULL,
    estadosnombre VARCHAR(50) NOT NULL,
    CONSTRAINT pk_estados PRIMARY KEY (idestados),
    CONSTRAINT fk_estpai FOREIGN KEY (pais_idpais) REFERENCES pais(idpais)
);

CREATE TABLE ciudad (
    idciudad          INT         NOT NULL IDENTITY(1,1),
    estados_idestados VARCHAR(6)  NOT NULL,
    nombre_ciudad     VARCHAR(50) NOT NULL,
    CONSTRAINT pk_ciudad PRIMARY KEY (idciudad),
    CONSTRAINT fk_ciudest FOREIGN KEY (estados_idestados) REFERENCES estados(idestados)
);

CREATE TABLE colonia (
    idcolonia       VARCHAR(10) NOT NULL,
    ciudad_idciudad INT         NOT NULL,
    nombrecolonia   VARCHAR(50) NOT NULL,
    CONSTRAINT pk_colonia PRIMARY KEY (idcolonia),
    CONSTRAINT fk_colciu FOREIGN KEY (ciudad_idciudad) REFERENCES ciudad(idciudad)
);

CREATE TABLE calle (
    idcalle           INT         NOT NULL IDENTITY(1,1),
    colonia_idcolonia VARCHAR(10) NOT NULL,
    nombrecalle       VARCHAR(100) NOT NULL,
    CONSTRAINT pk_calle PRIMARY KEY (idcalle),
    CONSTRAINT fk_calcol FOREIGN KEY (colonia_idcolonia) REFERENCES colonia(idcolonia)
);

-- 3. Entidades Principales
CREATE TABLE sucursales (
    idsucursal      INT          NOT NULL IDENTITY(1,1),
    calle_idcalle   INT          NOT NULL,
    nombre_sucursal VARCHAR(50)  NOT NULL,
    n_exterior      VARCHAR(10)  NOT NULL,
    n_interior      VARCHAR(10)  NULL,
    CONSTRAINT pk_sucursal PRIMARY KEY (idsucursal),
    CONSTRAINT fk_succal FOREIGN KEY (calle_idcalle) REFERENCES calle(idcalle)
);

CREATE TABLE Clientes (
    idClientes       INT          NOT NULL IDENTITY(1,1),
    calle_idcalle    INT          NOT NULL,
    Nombre           VARCHAR(50)  NULL,
    Apellido_Paterno VARCHAR(50)  NULL,
    Apellido_Materno VARCHAR(50)  NULL,
    FechaRegistro    DATE         DEFAULT GETDATE(),
    CONSTRAINT pk_Clientes PRIMARY KEY (idClientes),
    CONSTRAINT fk_clical FOREIGN KEY (calle_idcalle) REFERENCES calle(idcalle)
);

CREATE TABLE empleados (
    idempleados           INT          NOT NULL IDENTITY(1,1),
    calle_idcalle         INT          NOT NULL,
    sucursales_idsucursal INT          NOT NULL,
    nombre_empleado       VARCHAR(50)  NOT NULL,
    apellido_P            VARCHAR(50)  NOT NULL,
    apellido_m            VARCHAR(50)  NOT NULL,
    curp                  VARCHAR(18)  UNIQUE NOT NULL,
    rfc                   VARCHAR(13)  UNIQUE NOT NULL,
    puesto                VARCHAR(50)  NOT NULL,
    contrasena            VARCHAR(100) NULL,
    CONSTRAINT pk_empleados PRIMARY KEY (idempleados),
    CONSTRAINT fk_emplcal FOREIGN KEY (calle_idcalle) REFERENCES calle(idcalle),
    CONSTRAINT fk_empsuc FOREIGN KEY (sucursales_idsucursal) REFERENCES sucursales(idsucursal)
);

CREATE TABLE Videojuego (
    idVideojuego                  INT           NOT NULL IDENTITY(1,1),
    clasificacion_idclasificacion VARCHAR(5)    NOT NULL,
    Titulo                        VARCHAR(150)  NOT NULL,
    Precio                        DECIMAL(10,2) NOT NULL,
    FechaLanzamiento              DATE          NULL,
    CONSTRAINT pk_Videojuego PRIMARY KEY (idVideojuego),
    CONSTRAINT fk_vidcla FOREIGN KEY (clasificacion_idclasificacion) REFERENCES clasificacion(idclasificacion),
    CONSTRAINT chk_precio_vid CHECK (Precio > 0)
);

-- 4. Inventarios y Detalles
CREATE TABLE Plataforma (
    idPlataforma            VARCHAR(50) NOT NULL,
    Videojuego_idVideojuego INT         NOT NULL,
    Nombre                  VARCHAR(50) NULL,
    CONSTRAINT pk_Plataforma PRIMARY KEY (idPlataforma),
    CONSTRAINT fk_platvid FOREIGN KEY (Videojuego_idVideojuego) REFERENCES Videojuego(idVideojuego)
);

CREATE TABLE inventarios (
    idinventario            INT          NOT NULL IDENTITY(1,1),
    Plataforma_idPlataforma VARCHAR(50)  NOT NULL,
    sucursales_idsucursal   INT          NOT NULL,
    nombre_inventario       VARCHAR(50)  NULL,
    stock                   INT          NOT NULL,
    CONSTRAINT pk_inventarios PRIMARY KEY (idinventario),
    CONSTRAINT fk_invpla FOREIGN KEY (Plataforma_idPlataforma) REFERENCES Plataforma(idPlataforma),
    CONSTRAINT fk_invsuc FOREIGN KEY (sucursales_idsucursal) REFERENCES sucursales(idsucursal),
    CONSTRAINT chk_stock_min CHECK (stock >= 0)
);

-- 5. Ventas y Compras
CREATE TABLE Ventas (
    idVentas              INT           NOT NULL IDENTITY(1,1),
    sucursales_idsucursal INT           NOT NULL,
    empleados_idempleados INT           NOT NULL,
    Clientes_idClientes   INT           NOT NULL,
    FechaVenta            DATETIME      DEFAULT GETDATE(),
    Total                 DECIMAL(10,2) NOT NULL,
    MetodoPago            VARCHAR(30)   NOT NULL,
    CONSTRAINT pk_Ventas PRIMARY KEY (idVentas),
    CONSTRAINT fk_ventsuc FOREIGN KEY (sucursales_idsucursal) REFERENCES sucursales(idsucursal),
    CONSTRAINT fk_ventemp FOREIGN KEY (empleados_idempleados) REFERENCES empleados(idempleados),
    CONSTRAINT fk_ventcli FOREIGN KEY (Clientes_idClientes) REFERENCES Clientes(idClientes),
    CONSTRAINT chk_metodo_pago CHECK (MetodoPago IN ('Efectivo', 'Tarjeta', 'Transferencia'))
);

CREATE TABLE Detalle_Ventas (
    idDetalle                INT           NOT NULL IDENTITY(1,1),
    Ventas_idVentas          INT           NOT NULL,
    Videojuego_idVideojuego  INT           NOT NULL,
    Cantidad                 INT           NOT NULL,
    Precio_unitario          DECIMAL(10,2) NOT NULL,
    Subtotal                 DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_DetalleVentas PRIMARY KEY (idDetalle),
    CONSTRAINT fk_detven FOREIGN KEY (Ventas_idVentas) REFERENCES Ventas(idVentas),
    CONSTRAINT fk_detvid FOREIGN KEY (Videojuego_idVideojuego) REFERENCES Videojuego(idVideojuego),
    CONSTRAINT chk_cantidad_ven CHECK (Cantidad > 0)
);

-- 6. Contacto
CREATE TABLE telefono (
    idtelefono               INT         NOT NULL IDENTITY(1,1),
    proveedores_id_proveedor INT         NULL,
    empleados_idempleados    INT         NULL,
    sucursales_idsucursal    INT         NULL,
    Clientes_idClientes      INT         NULL,
    numerotelefono           VARCHAR(20) NOT NULL,
    CONSTRAINT pk_telefono PRIMARY KEY (idtelefono),
    CONSTRAINT fk_telemp FOREIGN KEY (empleados_idempleados) REFERENCES empleados(idempleados),
    CONSTRAINT fk_telsuc FOREIGN KEY (sucursales_idsucursal) REFERENCES sucursales(idsucursal),
    CONSTRAINT fk_telcli FOREIGN KEY (Clientes_idClientes) REFERENCES Clientes(idClientes),
    CONSTRAINT fk_telpro FOREIGN KEY (proveedores_id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE Correos (
    id_correo                INT          NOT NULL IDENTITY(1,1),
    Clientes_idClientes      INT          NULL,
    sucursales_idsucursal    INT          NULL,
    empleados_idempleados    INT          NULL,
    proveedores_id_proveedor INT          NULL,
    correo                   VARCHAR(100) NOT NULL,
    CONSTRAINT pk_Correos PRIMARY KEY (id_correo),
    CONSTRAINT fk_corcli FOREIGN KEY (Clientes_idClientes) REFERENCES Clientes(idClientes),
    CONSTRAINT fk_corsuc FOREIGN KEY (sucursales_idsucursal) REFERENCES sucursales(idsucursal),
    CONSTRAINT fk_coremp FOREIGN KEY (empleados_idempleados) REFERENCES empleados(idempleados),
    CONSTRAINT fk_corpro FOREIGN KEY (proveedores_id_proveedor) REFERENCES proveedores(id_proveedor)
);
