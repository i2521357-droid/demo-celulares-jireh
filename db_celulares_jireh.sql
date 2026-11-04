-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 15-10-2026 a las 23:41:00
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `db_celulares_jireh`
--
CREATE DATABASE IF NOT EXISTS `db_celulares_jireh` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `db_celulares_jireh`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `accesorio`
--

CREATE TABLE `accesorio` (
  `id` int(11) NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `marca` varchar(100) DEFAULT NULL,
  `modelo` varchar(100) DEFAULT NULL,
  `modelos_compatibles` varchar(255) DEFAULT NULL,
  `caracteristicas` varchar(255) DEFAULT NULL,
  `costo` decimal(10,2) NOT NULL,
  `precio_cliente` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `proveedor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `accesorio`
--

INSERT INTO `accesorio` (`id`, `tipo`, `marca`, `modelo`, `modelos_compatibles`, `caracteristicas`, `costo`, `precio_cliente`, `stock`, `proveedor_id`) VALUES
(1, 'AURICULARES', 'ROMAX', 'L21', NULL, 'INALÁMBRICO (BLUETOOTH)', 32.00, 65.00, 2, 4),
(2, 'AURICULARES', 'MICCELL', 'PRO 25', NULL, 'INALÁMBRICO (BLUETOOTH)', 41.00, 85.00, 2, 5),
(3, 'CARGADOR', 'VEX', '2DA GENERACIÓN GAN', NULL, 'CON CABLE | TIPO-C | CARGA RÁPIDA SEGUNDERO | 6A | 120W', 26.00, 55.00, 4, 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categoria_catalogo`
--

CREATE TABLE `categoria_catalogo` (
  `id` int(11) NOT NULL,
  `seccion` varchar(50) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categoria_catalogo`
--

INSERT INTO `categoria_catalogo` (`id`, `seccion`, `nombre`) VALUES
(1, 'TIPO_ACCESORIO', 'FUNDA CASE'),
(2, 'TIPO_ACCESORIO', 'MICA DE VIDRIO'),
(3, 'TIPO_ACCESORIO', 'MICA HIDROGEL'),
(4, 'TIPO_ACCESORIO', 'CABLE USB'),
(5, 'TIPO_ACCESORIO', 'CARGADOR'),
(6, 'TIPO_ACCESORIO', 'AURICULARES'),
(7, 'CALIDAD_REPUESTO', 'ORIGINAL'),
(8, 'CALIDAD_REPUESTO', 'AMOLED BORDE FINO'),
(9, 'CALIDAD_REPUESTO', 'OLED'),
(10, 'CALIDAD_REPUESTO', 'INCELL / GENÉRICA'),
(11, 'CALIDAD_REPUESTO', 'BATERÍA ORIGINAL'),
(12, 'CALIDAD_REPUESTO', 'ZÓCALO / FLEX CARGA'),
(13, 'MARCA_REPUESTO', 'XIAOMI'),
(14, 'MARCA_REPUESTO', 'SAMSUNG'),
(15, 'MARCA_REPUESTO', 'HONOR'),
(16, 'MARCA_REPUESTO', 'MOTOROLA'),
(17, 'MARCA_REPUESTO', 'APPLE'),
(18, 'MARCA_REPUESTO', 'REALME'),
(19, 'MARCA_REPUESTO', 'ZTE'),
(20, 'MARCA_REPUESTO', 'INFINIX');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `celular`
--

CREATE TABLE `celular` (
  `id` int(11) NOT NULL,
  `imei` varchar(15) NOT NULL,
  `imei2` varchar(15) DEFAULT NULL,
  `marca` varchar(100) NOT NULL,
  `modelo` varchar(100) NOT NULL,
  `codigo_modelo` varchar(100) DEFAULT NULL,
  `color` varchar(50) NOT NULL,
  `ram` varchar(20) NOT NULL,
  `rom` varchar(20) NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  `precio_cliente` decimal(10,2) NOT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `disponible` tinyint(1) DEFAULT NULL,
  `proveedor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `celular`
--

INSERT INTO `celular` (`id`, `imei`, `imei2`, `marca`, `modelo`, `codigo_modelo`, `color`, `ram`, `rom`, `costo`, `precio_cliente`, `estado`, `disponible`, `proveedor_id`) VALUES
(1, '357269438189357', NULL, 'SAMSUNG', 'A06', 'A065M', 'BLACK', '4 GB', '128 GB', 320.00, 470.00, 'NUEVO', 1, 6),
(2, '356746451354685', NULL, 'SAMSUNG', 'A06', 'A065M', 'BLACK', '4 GB', '128 GB', 320.00, 470.00, 'NUEVO', 1, 6),
(3, '863543216841305', '863543216841346', 'XIAOMI', 'REDMI A7 PRO', '25128RN17L', 'NEGRO', '4 GB', '128 GB', 380.00, 530.00, 'NUEVO', 1, 6),
(4, '863543216841468', '863543216841494', 'XIAOMI', 'REDMI A7 PRO', '25128RN17L', 'NEGRO', '4 GB', '64 GB', 380.00, 530.00, 'NUEVO', 0, 6);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_orden_repuesto`
--

CREATE TABLE `detalle_orden_repuesto` (
  `id` int(11) NOT NULL,
  `orden_id` int(11) NOT NULL,
  `repuesto_id` int(11) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_orden_repuesto`
--

INSERT INTO `detalle_orden_repuesto` (`id`, `orden_id`, `repuesto_id`, `descripcion`, `cantidad`, `precio_unitario`, `subtotal`) VALUES
(1, 1, 1, '⚙️ XIAOMI REDMI NOTE 11 (AMOLED BORDE FINO)', 1, 130.00, 130.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_venta`
--

CREATE TABLE `detalle_venta` (
  `id` int(11) NOT NULL,
  `venta_id` int(11) NOT NULL,
  `tipo_producto` varchar(50) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_venta`
--

INSERT INTO `detalle_venta` (`id`, `venta_id`, `tipo_producto`, `producto_id`, `descripcion`, `cantidad`, `precio_unitario`, `subtotal`) VALUES
(1, 1, 'CELULAR', 4, '📱 XIAOMI REDMI A7 PRO (4 GB / 64 GB) - IMEI: 863543216841468', 1, 530.00, 530.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `orden_servicio`
--

CREATE TABLE `orden_servicio` (
  `id` int(11) NOT NULL,
  `fecha_ingreso` datetime DEFAULT NULL,
  `documento_cliente` varchar(15) NOT NULL,
  `nombre_cliente` varchar(150) NOT NULL,
  `telefono_cliente` varchar(15) DEFAULT NULL,
  `marca` varchar(100) NOT NULL,
  `modelo` varchar(100) NOT NULL,
  `imei_serie` varchar(50) DEFAULT NULL,
  `patron_contrasena` varchar(50) DEFAULT NULL,
  `falla_reportada` text NOT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `costo_mano_obra` decimal(10,2) DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `acuenta` decimal(10,2) DEFAULT NULL,
  `saldo` decimal(10,2) DEFAULT NULL,
  `personal_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `orden_servicio`
--

INSERT INTO `orden_servicio` (`id`, `fecha_ingreso`, `documento_cliente`, `nombre_cliente`, `telefono_cliente`, `marca`, `modelo`, `imei_serie`, `patron_contrasena`, `falla_reportada`, `estado`, `costo_mano_obra`, `total`, `acuenta`, `saldo`, `personal_id`) VALUES
(1, '2026-10-09 01:10:02', '73233377', 'DANIEL RICHARD DIAZ VICAÑA', '923139841', 'XIAOMI', 'REDMI NOTE 11', 'NO VISIBLE', '1-5-9-3-7', 'PANTALLA ROTA', 'ENTREGADO', 0.00, 130.00, 130.00, 0.00, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `personal`
--

CREATE TABLE `personal` (
  `id` int(11) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `rol_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `personal`
--

INSERT INTO `personal` (`id`, `nombres`, `apellidos`, `usuario`, `password_hash`, `rol_id`) VALUES
(1, 'Daniel', 'Diaz', 'elmasperrón', '$2b$12$g0ooivMhhzhRtQOei.QHCeflyf.pBPlP/VKx7xBEWZUdOj3nWR72O', 1),
(3, 'ALEX LEONARDO', 'VEGA CCENTE', 'alex.vega', '$2b$12$8WRARFKodEqLdFVzxHUD6uRwQ0cmaqSreJW8Sok9SlICFPdsEqzG2', 1),
(4, 'JHON JOEL', 'VICAÑA MAPELE', 'jhon.vicana', '$2b$12$PFqanE.SPeUrhP.UHwGmuOgzj4KaaS9Vfry1aR0t71OWnEi7PTRjG', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedor`
--

CREATE TABLE `proveedor` (
  `id` int(11) NOT NULL,
  `razon_social` varchar(150) NOT NULL,
  `ruc` varchar(11) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proveedor`
--

INSERT INTO `proveedor` (`id`, `razon_social`, `ruc`, `telefono`) VALUES
(1, 'CHINAPHONE', NULL, NULL),
(2, 'MICAS PERU SAC', NULL, NULL),
(3, 'CARCASAS.COM SAC', NULL, NULL),
(4, 'ROMAX PERU SAC', NULL, NULL),
(5, 'VEX PERU SAC', NULL, NULL),
(6, 'TRADING MOBILES IMPORT SAC', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `repuesto`
--

CREATE TABLE `repuesto` (
  `id` int(11) NOT NULL,
  `marca` varchar(100) NOT NULL,
  `modelo` varchar(100) NOT NULL,
  `modelos_compatibles` varchar(255) DEFAULT NULL,
  `calidad` varchar(50) NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  `precio_cliente` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `proveedor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `repuesto`
--

INSERT INTO `repuesto` (`id`, `marca`, `modelo`, `modelos_compatibles`, `calidad`, `costo`, `precio_cliente`, `stock`, `proveedor_id`) VALUES
(1, 'XIAOMI', 'REDMI NOTE 11', 'REDMI NOTE 11S, REDMI NOTE 12S', 'AMOLED BORDE FINO', 80.00, 130.00, 14, 1),
(2, 'SAMSUNG', 'GALAXY A02', 'GALAXY A12, GALAXY A32 5G, GALAXY M12', 'INCELL / GENÉRICA', 32.00, 85.00, 12, 1),
(3, 'XIAOMI', 'REDMI NOTE 10', 'REDMI NOTE 10S', 'ZÓCALO / FLEX CARGA', 20.00, 45.00, 1, 1),
(4, 'MOTOROLA', 'MOTOROLA G31', NULL, 'AMOLED BORDE FINO', 80.00, 130.00, 2, 1),
(5, 'HONOR', 'HONOR X7B', NULL, 'BATERÍA ORIGINAL', 49.00, 100.00, 1, NULL),
(6, 'SAMSUNG', 'S22 ULTRA', NULL, 'BATERÍA ORIGINAL', 46.00, 100.00, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--

CREATE TABLE `rol` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `rol`
--

INSERT INTO `rol` (`id`, `nombre`) VALUES
(1, 'ADMINISTRADOR'),
(2, 'TRABAJADOR');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `venta`
--

CREATE TABLE `venta` (
  `id` int(11) NOT NULL,
  `fecha_hora` datetime DEFAULT NULL,
  `tipo_comprobante` varchar(20) NOT NULL,
  `documento_cliente` varchar(15) NOT NULL,
  `nombre_cliente` varchar(150) NOT NULL,
  `metodo_pago` varchar(50) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `personal_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `venta`
--

INSERT INTO `venta` (`id`, `fecha_hora`, `tipo_comprobante`, `documento_cliente`, `nombre_cliente`, `metodo_pago`, `total`, `personal_id`) VALUES
(1, '2026-10-15 21:37:41', 'BOLETA', '73233377', 'DANIEL RICHARD DIAZ VICAÑA', 'EFECTIVO', 530.00, 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `accesorio`
--
ALTER TABLE `accesorio`
  ADD PRIMARY KEY (`id`),
  ADD KEY `proveedor_id` (`proveedor_id`);

--
-- Indices de la tabla `categoria_catalogo`
--
ALTER TABLE `categoria_catalogo`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `celular`
--
ALTER TABLE `celular`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `imei` (`imei`),
  ADD KEY `proveedor_id` (`proveedor_id`);

--
-- Indices de la tabla `detalle_orden_repuesto`
--
ALTER TABLE `detalle_orden_repuesto`
  ADD PRIMARY KEY (`id`),
  ADD KEY `orden_id` (`orden_id`);

--
-- Indices de la tabla `detalle_venta`
--
ALTER TABLE `detalle_venta`
  ADD PRIMARY KEY (`id`),
  ADD KEY `venta_id` (`venta_id`);

--
-- Indices de la tabla `orden_servicio`
--
ALTER TABLE `orden_servicio`
  ADD PRIMARY KEY (`id`),
  ADD KEY `personal_id` (`personal_id`);

--
-- Indices de la tabla `personal`
--
ALTER TABLE `personal`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario` (`usuario`),
  ADD KEY `rol_id` (`rol_id`);

--
-- Indices de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ruc` (`ruc`);

--
-- Indices de la tabla `repuesto`
--
ALTER TABLE `repuesto`
  ADD PRIMARY KEY (`id`),
  ADD KEY `proveedor_id` (`proveedor_id`);

--
-- Indices de la tabla `rol`
--
ALTER TABLE `rol`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `venta`
--
ALTER TABLE `venta`
  ADD PRIMARY KEY (`id`),
  ADD KEY `personal_id` (`personal_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `accesorio`
--
ALTER TABLE `accesorio`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `categoria_catalogo`
--
ALTER TABLE `categoria_catalogo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `celular`
--
ALTER TABLE `celular`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `detalle_orden_repuesto`
--
ALTER TABLE `detalle_orden_repuesto`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `detalle_venta`
--
ALTER TABLE `detalle_venta`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `orden_servicio`
--
ALTER TABLE `orden_servicio`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `personal`
--
ALTER TABLE `personal`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `repuesto`
--
ALTER TABLE `repuesto`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `rol`
--
ALTER TABLE `rol`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `venta`
--
ALTER TABLE `venta`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `accesorio`
--
ALTER TABLE `accesorio`
  ADD CONSTRAINT `accesorio_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedor` (`id`);

--
-- Filtros para la tabla `celular`
--
ALTER TABLE `celular`
  ADD CONSTRAINT `celular_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedor` (`id`);

--
-- Filtros para la tabla `detalle_orden_repuesto`
--
ALTER TABLE `detalle_orden_repuesto`
  ADD CONSTRAINT `detalle_orden_repuesto_ibfk_1` FOREIGN KEY (`orden_id`) REFERENCES `orden_servicio` (`id`);

--
-- Filtros para la tabla `detalle_venta`
--
ALTER TABLE `detalle_venta`
  ADD CONSTRAINT `detalle_venta_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `venta` (`id`);

--
-- Filtros para la tabla `orden_servicio`
--
ALTER TABLE `orden_servicio`
  ADD CONSTRAINT `orden_servicio_ibfk_1` FOREIGN KEY (`personal_id`) REFERENCES `personal` (`id`);

--
-- Filtros para la tabla `personal`
--
ALTER TABLE `personal`
  ADD CONSTRAINT `personal_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`);

--
-- Filtros para la tabla `repuesto`
--
ALTER TABLE `repuesto`
  ADD CONSTRAINT `repuesto_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedor` (`id`);

--
-- Filtros para la tabla `venta`
--
ALTER TABLE `venta`
  ADD CONSTRAINT `venta_ibfk_1` FOREIGN KEY (`personal_id`) REFERENCES `personal` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
