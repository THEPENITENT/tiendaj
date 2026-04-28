-- ============================================
-- TIENDAJ - Schema para MariaDB
-- Tienda de Videojuegos
-- ============================================

CREATE DATABASE IF NOT EXISTS tiendaj CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE tiendaj;

-- 1. Catálogos
CREATE TABLE IF NOT EXISTS clasificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS plataforma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- 2. Videojuegos
CREATE TABLE IF NOT EXISTS videojuego (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    precio DECIMAL(10,2) NOT NULL CHECK (precio > 0),
    clasificacion_id INT NOT NULL,
    plataforma_id INT NOT NULL,
    fecha_lanzamiento DATE NULL,
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clasificacion_id) REFERENCES clasificacion(id),
    FOREIGN KEY (plataforma_id) REFERENCES plataforma(id)
);

-- 3. Clientes
CREATE TABLE IF NOT EXISTS cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NULL,
    email VARCHAR(100) NULL,
    telefono VARCHAR(20) NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Ventas
CREATE TABLE IF NOT EXISTS venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Transferencia') NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id)
);

CREATE TABLE IF NOT EXISTS detalle_venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    videojuego_id INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES venta(id) ON DELETE CASCADE,
    FOREIGN KEY (videojuego_id) REFERENCES videojuego(id)
);

-- ============================================
-- Datos de ejemplo
-- ============================================

INSERT INTO clasificacion (nombre) VALUES
('E - Everyone'), ('T - Teen'), ('M - Mature'), ('E10+ - Everyone 10+');

INSERT INTO plataforma (nombre) VALUES
('PlayStation 5'), ('Xbox Series X'), ('Nintendo Switch'), ('PC'), ('PlayStation 4');

INSERT INTO videojuego (titulo, precio, clasificacion_id, plataforma_id, fecha_lanzamiento, stock) VALUES
('The Legend of Zelda: Tears of the Kingdom', 1399.00, 1, 3, '2023-05-12', 25),
('God of War Ragnarök', 1299.00, 3, 1, '2022-11-09', 15),
('FIFA 25', 1199.00, 1, 4, '2024-09-27', 40),
('Resident Evil 4 Remake', 999.00, 3, 1, '2023-03-24', 20),
('Mario Kart 8 Deluxe', 1099.00, 1, 3, '2017-04-28', 30),
('Elden Ring', 1199.00, 3, 4, '2022-02-25', 18),
('Minecraft', 499.00, 1, 4, '2011-11-18', 50),
('Balatro', 299.00, 2, 4, '2024-02-20', 35),
('Cyberpunk 2077', 899.00, 3, 4, '2020-12-10', 22),
('Animal Crossing: New Horizons', 1099.00, 1, 3, '2020-03-20', 28);

INSERT INTO cliente (nombre, apellido_paterno, apellido_materno, email, telefono) VALUES
('Angel', 'García', 'López', 'angel@mail.com', '844-123-4567'),
('Carlos', 'Martínez', 'Reyes', 'carlos@mail.com', '844-234-5678'),
('María', 'Rodríguez', 'Sánchez', 'maria@mail.com', '844-345-6789'),
('Juan', 'Hernández', 'Torres', 'juan@mail.com', '844-456-7890'),
('Sofía', 'López', 'Díaz', 'sofia@mail.com', '844-567-8901');

INSERT INTO venta (cliente_id, total, metodo_pago) VALUES
(1, 1399.00, 'Tarjeta'),
(2, 2498.00, 'Efectivo'),
(3, 499.00, 'Transferencia');

INSERT INTO detalle_venta (venta_id, videojuego_id, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 1, 1399.00, 1399.00),
(2, 4, 1, 999.00, 999.00),
(2, 6, 1, 1199.00, 1199.00),
(2, 8, 1, 299.00, 299.00),
(3, 7, 1, 499.00, 499.00);
