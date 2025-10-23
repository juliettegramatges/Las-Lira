# Diseño de Base de Datos - Las-Lira 🗄️

## Diagrama de Entidades y Relaciones

### Tablas Principales

#### 1. **flores**
```sql
CREATE TABLE flores (
    id VARCHAR(10) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    proveedor_id VARCHAR(10),
    costo_unitario DECIMAL(10,2) NOT NULL,
    cantidad_stock INT NOT NULL DEFAULT 0,
    bodega_id INT NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    fecha_actualizacion DATE,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    FOREIGN KEY (bodega_id) REFERENCES bodegas(id)
);
```

#### 2. **contenedores**
```sql
CREATE TABLE contenedores (
    id VARCHAR(10) PRIMARY KEY,
    tipo ENUM('Florero', 'Macetero', 'Canasto') NOT NULL,
    material VARCHAR(30) NOT NULL,
    forma VARCHAR(30) NOT NULL,
    tamano VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    costo DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    bodega_id INT NOT NULL,
    fecha_actualizacion DATE,
    FOREIGN KEY (bodega_id) REFERENCES bodegas(id)
);
```

#### 3. **bodegas**
```sql
CREATE TABLE bodegas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(200),
    encargado VARCHAR(100),
    telefono VARCHAR(20),
    activa BOOLEAN DEFAULT TRUE
);
```

#### 4. **productos**
```sql
CREATE TABLE productos (
    id VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo_arreglo ENUM('Con Florero', 'Con Macetero', 'Con Canasto', 'Sin Contenedor', 'Con Caja') NOT NULL,
    paleta_colores VARCHAR(200),
    cantidad_flores_min INT,
    cantidad_flores_max INT,
    precio_venta DECIMAL(10,2) NOT NULL,
    imagen_url VARCHAR(500),
    disponible_shopify BOOLEAN DEFAULT TRUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. **recetas_productos**
```sql
CREATE TABLE recetas_productos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    producto_id VARCHAR(10) NOT NULL,
    insumo_tipo ENUM('Flor', 'Contenedor') NOT NULL,
    insumo_id VARCHAR(10) NOT NULL,
    cantidad INT NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    es_opcional BOOLEAN DEFAULT FALSE,
    notas TEXT,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
    -- insumo_id puede referenciar flores O contenedores según insumo_tipo
);
```

#### 6. **pedidos**
```sql
CREATE TABLE pedidos (
    id VARCHAR(20) PRIMARY KEY,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    canal ENUM('Shopify', 'WhatsApp') NOT NULL,
    cliente_nombre VARCHAR(100) NOT NULL,
    cliente_telefono VARCHAR(20) NOT NULL,
    cliente_email VARCHAR(100),
    producto_id VARCHAR(10), -- NULL para pedidos personalizados
    descripcion_personalizada TEXT,
    estado ENUM('Recibido', 'En Preparación', 'Listo', 'Despachado', 'Entregado', 'Cancelado') DEFAULT 'Recibido',
    precio_total DECIMAL(10,2) NOT NULL,
    direccion_entrega VARCHAR(300) NOT NULL,
    comuna VARCHAR(50),
    fecha_entrega DATE NOT NULL,
    hora_entrega TIME,
    notas TEXT,
    usuario_id INT, -- quién registró el pedido
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

#### 7. **pedidos_insumos**
```sql
CREATE TABLE pedidos_insumos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pedido_id VARCHAR(20) NOT NULL,
    insumo_tipo ENUM('Flor', 'Contenedor') NOT NULL,
    insumo_id VARCHAR(10) NOT NULL,
    cantidad INT NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    costo_total DECIMAL(10,2) NOT NULL,
    descontado_stock BOOLEAN DEFAULT FALSE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);
```

#### 8. **proveedores**
```sql
CREATE TABLE proveedores (
    id VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    especialidad TEXT,
    dias_entrega VARCHAR(200),
    notas TEXT,
    activo BOOLEAN DEFAULT TRUE
);
```

#### 9. **usuarios**
```sql
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('Admin', 'Vendedor', 'Preparador') NOT NULL,
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP
);
```

#### 10. **historial_estados**
```sql
CREATE TABLE historial_estados (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pedido_id VARCHAR(20) NOT NULL,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    usuario_id INT,
    comentario TEXT,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

#### 11. **movimientos_inventario**
```sql
CREATE TABLE movimientos_inventario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tipo_movimiento ENUM('Entrada', 'Salida', 'Ajuste', 'Pedido') NOT NULL,
    insumo_tipo ENUM('Flor', 'Contenedor') NOT NULL,
    insumo_id VARCHAR(10) NOT NULL,
    cantidad INT NOT NULL,
    costo_unitario DECIMAL(10,2),
    bodega_id INT NOT NULL,
    pedido_id VARCHAR(20), -- si es por un pedido
    usuario_id INT,
    motivo VARCHAR(200),
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bodega_id) REFERENCES bodegas(id),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

## Índices para Optimización

```sql
-- Índices para búsquedas frecuentes
CREATE INDEX idx_pedidos_fecha ON pedidos(fecha_pedido);
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_canal ON pedidos(canal);
CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_telefono);
CREATE INDEX idx_flores_tipo_color ON flores(tipo, color);
CREATE INDEX idx_flores_bodega ON flores(bodega_id);
CREATE INDEX idx_contenedores_tipo ON contenedores(tipo);
CREATE INDEX idx_movimientos_fecha ON movimientos_inventario(fecha_movimiento);
```

## Vistas Útiles

### Vista de Stock Total por Producto
```sql
CREATE VIEW vista_stock_total AS
SELECT 
    tipo,
    color,
    SUM(cantidad_stock) as stock_total,
    GROUP_CONCAT(CONCAT('Bodega ', bodega_id, ': ', cantidad_stock)) as detalle_bodegas
FROM flores
GROUP BY tipo, color;
```

### Vista de Pedidos Pendientes
```sql
CREATE VIEW vista_pedidos_pendientes AS
SELECT 
    p.id,
    p.fecha_pedido,
    p.canal,
    p.cliente_nombre,
    p.estado,
    p.fecha_entrega,
    CASE 
        WHEN p.producto_id IS NOT NULL THEN pr.nombre
        ELSE 'Pedido Personalizado'
    END as producto,
    p.precio_total
FROM pedidos p
LEFT JOIN productos pr ON p.producto_id = pr.id
WHERE p.estado NOT IN ('Entregado', 'Cancelado')
ORDER BY p.fecha_entrega ASC, p.fecha_pedido ASC;
```

### Vista de Costo Real de Pedidos
```sql
CREATE VIEW vista_costos_pedidos AS
SELECT 
    p.id as pedido_id,
    p.precio_total as precio_venta,
    SUM(pi.costo_total) as costo_insumos,
    (p.precio_total - SUM(pi.costo_total)) as ganancia_bruta,
    ((p.precio_total - SUM(pi.costo_total)) / p.precio_total * 100) as margen_porcentaje
FROM pedidos p
LEFT JOIN pedidos_insumos pi ON p.id = pi.pedido_id
GROUP BY p.id;
```

## Funciones y Procedimientos Almacenados

### Función: Verificar Stock Disponible
```sql
DELIMITER //
CREATE FUNCTION verificar_stock_producto(
    p_producto_id VARCHAR(10)
) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE hay_stock BOOLEAN DEFAULT TRUE;
    DECLARE v_insumo_id VARCHAR(10);
    DECLARE v_cantidad_necesaria INT;
    DECLARE v_stock_actual INT;
    DECLARE v_insumo_tipo VARCHAR(20);
    DECLARE done INT DEFAULT FALSE;
    
    DECLARE cur CURSOR FOR 
        SELECT insumo_id, cantidad, insumo_tipo 
        FROM recetas_productos 
        WHERE producto_id = p_producto_id AND es_opcional = FALSE;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    verificar_loop: LOOP
        FETCH cur INTO v_insumo_id, v_cantidad_necesaria, v_insumo_tipo;
        
        IF done THEN
            LEAVE verificar_loop;
        END IF;
        
        IF v_insumo_tipo = 'Flor' THEN
            SELECT SUM(cantidad_stock) INTO v_stock_actual 
            FROM flores WHERE id = v_insumo_id;
        ELSE
            SELECT stock INTO v_stock_actual 
            FROM contenedores WHERE id = v_insumo_id;
        END IF;
        
        IF v_stock_actual < v_cantidad_necesaria THEN
            SET hay_stock = FALSE;
            LEAVE verificar_loop;
        END IF;
    END LOOP;
    
    CLOSE cur;
    RETURN hay_stock;
END //
DELIMITER ;
```

### Procedimiento: Descontar Stock de Pedido
```sql
DELIMITER //
CREATE PROCEDURE descontar_stock_pedido(
    IN p_pedido_id VARCHAR(20),
    IN p_usuario_id INT
)
BEGIN
    DECLARE v_insumo_id VARCHAR(10);
    DECLARE v_cantidad INT;
    DECLARE v_insumo_tipo VARCHAR(20);
    DECLARE done INT DEFAULT FALSE;
    
    DECLARE cur CURSOR FOR 
        SELECT insumo_id, cantidad, insumo_tipo 
        FROM pedidos_insumos 
        WHERE pedido_id = p_pedido_id AND descontado_stock = FALSE;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    START TRANSACTION;
    
    OPEN cur;
    
    descuento_loop: LOOP
        FETCH cur INTO v_insumo_id, v_cantidad, v_insumo_tipo;
        
        IF done THEN
            LEAVE descuento_loop;
        END IF;
        
        -- Descontar del inventario
        IF v_insumo_tipo = 'Flor' THEN
            UPDATE flores 
            SET cantidad_stock = cantidad_stock - v_cantidad,
                fecha_actualizacion = CURRENT_DATE
            WHERE id = v_insumo_id;
        ELSE
            UPDATE contenedores 
            SET stock = stock - v_cantidad,
                fecha_actualizacion = CURRENT_DATE
            WHERE id = v_insumo_id;
        END IF;
        
        -- Registrar movimiento
        INSERT INTO movimientos_inventario 
            (tipo_movimiento, insumo_tipo, insumo_id, cantidad, pedido_id, usuario_id, motivo)
        VALUES 
            ('Pedido', v_insumo_tipo, v_insumo_id, v_cantidad, p_pedido_id, p_usuario_id, 
             CONCAT('Descuento por pedido ', p_pedido_id));
        
        -- Marcar como descontado
        UPDATE pedidos_insumos 
        SET descontado_stock = TRUE 
        WHERE pedido_id = p_pedido_id AND insumo_id = v_insumo_id;
        
    END LOOP;
    
    CLOSE cur;
    COMMIT;
END //
DELIMITER ;
```

### Procedimiento: Calcular Costo Estimado
```sql
DELIMITER //
CREATE PROCEDURE calcular_costo_estimado(
    IN p_flores_json JSON,
    IN p_contenedor_id VARCHAR(10),
    OUT p_costo_total DECIMAL(10,2)
)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE n INT;
    DECLARE v_flor_tipo VARCHAR(50);
    DECLARE v_flor_color VARCHAR(30);
    DECLARE v_cantidad INT;
    DECLARE v_costo_flor DECIMAL(10,2);
    DECLARE v_costo_contenedor DECIMAL(10,2);
    
    SET p_costo_total = 0;
    SET n = JSON_LENGTH(p_flores_json);
    
    -- Calcular costo de flores
    WHILE i < n DO
        SET v_flor_tipo = JSON_UNQUOTE(JSON_EXTRACT(p_flores_json, CONCAT('$[', i, '].tipo')));
        SET v_flor_color = JSON_UNQUOTE(JSON_EXTRACT(p_flores_json, CONCAT('$[', i, '].color')));
        SET v_cantidad = JSON_EXTRACT(p_flores_json, CONCAT('$[', i, '].cantidad'));
        
        SELECT costo_unitario INTO v_costo_flor 
        FROM flores 
        WHERE tipo = v_flor_tipo AND color = v_flor_color 
        ORDER BY costo_unitario ASC 
        LIMIT 1;
        
        SET p_costo_total = p_costo_total + (v_costo_flor * v_cantidad);
        SET i = i + 1;
    END WHILE;
    
    -- Agregar costo del contenedor
    IF p_contenedor_id IS NOT NULL THEN
        SELECT costo INTO v_costo_contenedor 
        FROM contenedores 
        WHERE id = p_contenedor_id;
        
        SET p_costo_total = p_costo_total + v_costo_contenedor;
    END IF;
    
END //
DELIMITER ;
```

## Triggers

### Trigger: Actualizar historial de estados
```sql
DELIMITER //
CREATE TRIGGER trigger_historial_estado
AFTER UPDATE ON pedidos
FOR EACH ROW
BEGIN
    IF OLD.estado != NEW.estado THEN
        INSERT INTO historial_estados (pedido_id, estado_anterior, estado_nuevo, usuario_id)
        VALUES (NEW.id, OLD.estado, NEW.estado, NEW.usuario_id);
    END IF;
END //
DELIMITER ;
```

### Trigger: Alertar stock bajo
```sql
DELIMITER //
CREATE TRIGGER trigger_alerta_stock_bajo
AFTER UPDATE ON flores
FOR EACH ROW
BEGIN
    IF NEW.cantidad_stock < 10 AND OLD.cantidad_stock >= 10 THEN
        INSERT INTO alertas (tipo, mensaje, nivel, fecha)
        VALUES ('Stock Bajo', 
                CONCAT('Stock bajo de ', NEW.tipo, ' ', NEW.color, ': ', NEW.cantidad_stock, ' unidades'),
                'Warning',
                NOW());
    END IF;
END //
DELIMITER ;
```

## Datos Iniciales

```sql
-- Bodegas
INSERT INTO bodegas (nombre, direccion, encargado) VALUES
('Bodega 1', 'Principal - Centro', 'María González'),
('Bodega 2', 'Secundaria - Providencia', 'Carlos Pérez');

-- Usuario Admin por defecto
INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES
('Administrador', 'admin@laslira.cl', '$2b$10$...', 'Admin');
```

## Consideraciones de Seguridad

1. **Contraseñas**: Usar bcrypt o argon2 para hashear
2. **Tokens**: JWT para autenticación de sesiones
3. **Roles**: Admin, Vendedor, Preparador con permisos diferentes
4. **Auditoría**: Tabla de movimientos registra todos los cambios
5. **Backup**: Respaldos diarios automáticos

## Escalabilidad

- Particionamiento de tabla `pedidos` por fecha
- Índices parciales para consultas frecuentes
- Caché de productos y stock en Redis
- Replicación para alta disponibilidad

