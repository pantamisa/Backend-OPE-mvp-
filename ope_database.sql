-- =============================================================================
-- OpE — Sistema de Gestión y Monitoreo de Flota
-- Base de datos PostgreSQL compatible con Django ORM
-- Entregable #2 — Diseño de Sistemas de Información — ITM 2026
-- =============================================================================
-- Uso: psql -U postgres -d ope_db -f ope_database.sql
-- O desde Django: python manage.py migrate  (usando los modelos equivalentes)
-- =============================================================================

-- Crear base de datos (ejecutar como superusuario si aún no existe)
-- CREATE DATABASE ope_db ENCODING 'UTF8' LC_COLLATE 'es_CO.UTF-8' LC_CTYPE 'es_CO.UTF-8' TEMPLATE template0;
-- \c ope_db

BEGIN;

-- =============================================================================
-- EXTENSIONES
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- búsqueda de texto por similitud

-- =============================================================================
-- TABLAS DE AUTENTICACIÓN Y USUARIOS (Django auth + extensión de roles)
-- =============================================================================

-- Tabla de roles del sistema
CREATE TABLE IF NOT EXISTS auth_rol (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(50)  NOT NULL UNIQUE,  -- admin_flota | admin_contable | tecnico | conductor
    descripcion TEXT
);

-- Insertar roles base
INSERT INTO auth_rol (nombre, descripcion) VALUES
    ('admin_flota',     'Administrador de flota: gestiona vehículos, conductores y contratos'),
    ('admin_contable',  'Administrador contable: accede a reportes financieros y facturación'),
    ('tecnico',         'Técnico de mantenimiento: registra y gestiona servicios'),
    ('conductor',       'Conductor / arrendatario: consulta su renta activa y horas')
ON CONFLICT (nombre) DO NOTHING;

-- Extensión del usuario Django (profile)
-- Nota: Django crea auth_user automáticamente con migrate.
-- Esta tabla extiende ese usuario con el rol del sistema.
CREATE TABLE IF NOT EXISTS fleet_perfil_usuario (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    rol_id      INTEGER NOT NULL REFERENCES auth_rol(id),
    telefono    VARCHAR(20),
    activo      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- MÓDULO DE FLOTA — VEHÍCULOS
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_vehiculo (
    id              SERIAL PRIMARY KEY,
    placa           VARCHAR(10)     NOT NULL,
    modelo          VARCHAR(100)    NOT NULL,
    marca           VARCHAR(80)     NOT NULL DEFAULT '',
    anio            SMALLINT        NOT NULL CHECK (anio > 1900 AND anio <= EXTRACT(YEAR FROM NOW()) + 1),
    tipo            VARCHAR(20)     NOT NULL DEFAULT 'particular',
                                    -- particular | bus | camion | motocicleta | furgon
    capacidad       SMALLINT        NOT NULL DEFAULT 1 CHECK (capacidad > 0),
    color           VARCHAR(40),
    numero_motor    VARCHAR(50),
    numero_chasis   VARCHAR(50),
    km_inicial      DECIMAL(12,2)   NOT NULL DEFAULT 0 CHECK (km_inicial >= 0),
    km_acumulado    DECIMAL(12,2)   NOT NULL DEFAULT 0 CHECK (km_acumulado >= 0),
    estado          VARCHAR(25)     NOT NULL DEFAULT 'disponible',
                                    -- disponible | en_renta | mantenimiento | fuera_de_servicio
    fecha_registro  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fleet_vehiculo_placa_unique UNIQUE (placa),
    CONSTRAINT fleet_vehiculo_estado_check CHECK (
        estado IN ('disponible', 'en_renta', 'mantenimiento', 'fuera_de_servicio')
    ),
    CONSTRAINT fleet_vehiculo_tipo_check CHECK (
        tipo IN ('particular', 'bus', 'camion', 'motocicleta', 'furgon')
    )
);

-- Índices para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_vehiculo_estado  ON fleet_vehiculo (estado);
CREATE INDEX IF NOT EXISTS idx_vehiculo_placa   ON fleet_vehiculo USING gin (placa gin_trgm_ops);

-- =============================================================================
-- MÓDULO DE CONDUCTORES
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_conductor (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER UNIQUE REFERENCES auth_user(id) ON DELETE SET NULL,
    cedula          VARCHAR(20)     NOT NULL,
    nombre          VARCHAR(200)    NOT NULL,
    apellido        VARCHAR(200)    NOT NULL DEFAULT '',
    num_licencia    VARCHAR(30)     NOT NULL,
    categoria_licencia VARCHAR(10)  DEFAULT 'B1',  -- B1, B2, B3, C1, C2, C3
    fecha_venc_licencia DATE,
    telefono        VARCHAR(20),
    email           VARCHAR(254),
    estado          VARCHAR(20)     NOT NULL DEFAULT 'activo',
                                    -- activo | inactivo | suspendido
    horas_hoy       DECIMAL(5,2)    NOT NULL DEFAULT 0 CHECK (horas_hoy >= 0),
    horas_totales   DECIMAL(10,2)   NOT NULL DEFAULT 0 CHECK (horas_totales >= 0),
    limite_horas_dia DECIMAL(4,2)   NOT NULL DEFAULT 8.00,  -- RN-02: máx horas/día
    fecha_registro  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fleet_conductor_cedula_unique    UNIQUE (cedula),
    CONSTRAINT fleet_conductor_licencia_unique  UNIQUE (num_licencia),
    CONSTRAINT fleet_conductor_estado_check CHECK (
        estado IN ('activo', 'inactivo', 'suspendido')
    )
);

CREATE INDEX IF NOT EXISTS idx_conductor_estado ON fleet_conductor (estado);
CREATE INDEX IF NOT EXISTS idx_conductor_cedula ON fleet_conductor (cedula);

-- =============================================================================
-- MÓDULO DE CONTRATOS / RENTAS
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_contrato (
    id               SERIAL PRIMARY KEY,
    numero_contrato  VARCHAR(25)     NOT NULL,  -- CTR-YYYYMMDD-0001
    vehiculo_id      INTEGER         NOT NULL REFERENCES fleet_vehiculo(id) ON DELETE RESTRICT,
    conductor_id     INTEGER         NOT NULL REFERENCES fleet_conductor(id) ON DELETE RESTRICT,
    creado_por_id    INTEGER         REFERENCES auth_user(id) ON DELETE SET NULL,

    -- Tarifa (patrón Strategy: el tipo determina qué clase concreta usar)
    tipo_tarifa      VARCHAR(10)     NOT NULL DEFAULT 'dia',
                                     -- hora | dia | km
    tarifa_valor     DECIMAL(12,2)   NOT NULL CHECK (tarifa_valor > 0),

    -- Kilometraje
    km_inicial       DECIMAL(12,2)   NOT NULL CHECK (km_inicial >= 0),
    km_final         DECIMAL(12,2)   CHECK (km_final >= km_inicial),  -- NULL hasta cerrar

    -- Fechas
    fecha_inicio     TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_fin        TIMESTAMP WITH TIME ZONE,  -- NULL hasta cerrar

    -- Costo calculado por Strategy al cerrar
    costo_subtotal   DECIMAL(14,2)   CHECK (costo_subtotal >= 0),
    costo_penalizaciones DECIMAL(14,2) NOT NULL DEFAULT 0,
    costo_total      DECIMAL(14,2)   CHECK (costo_total >= 0),

    -- Estado
    estado           VARCHAR(15)     NOT NULL DEFAULT 'activa',
                                     -- activa | cerrada | cancelada

    -- Notas
    observaciones    TEXT,

    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fleet_contrato_numero_unique UNIQUE (numero_contrato),
    CONSTRAINT fleet_contrato_tipo_tarifa_check CHECK (
        tipo_tarifa IN ('hora', 'dia', 'km')
    ),
    CONSTRAINT fleet_contrato_estado_check CHECK (
        estado IN ('activa', 'cerrada', 'cancelada')
    )
);

-- RN-01: un vehículo no puede tener más de una renta activa
CREATE UNIQUE INDEX IF NOT EXISTS idx_contrato_vehiculo_activo
    ON fleet_contrato (vehiculo_id)
    WHERE estado = 'activa';

CREATE INDEX IF NOT EXISTS idx_contrato_estado       ON fleet_contrato (estado);
CREATE INDEX IF NOT EXISTS idx_contrato_conductor    ON fleet_contrato (conductor_id);
CREATE INDEX IF NOT EXISTS idx_contrato_vehiculo     ON fleet_contrato (vehiculo_id);
CREATE INDEX IF NOT EXISTS idx_contrato_fecha_inicio ON fleet_contrato (fecha_inicio);

-- =============================================================================
-- MÓDULO DE FACTURACIÓN
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_factura (
    id              SERIAL PRIMARY KEY,
    contrato_id     INTEGER         NOT NULL UNIQUE REFERENCES fleet_contrato(id) ON DELETE RESTRICT,
    numero_factura  VARCHAR(25)     NOT NULL UNIQUE,  -- FAC-YYYYMMDD-0001
    monto           DECIMAL(14,2)   NOT NULL CHECK (monto >= 0),
    fecha_emision   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    exportada       BOOLEAN         NOT NULL DEFAULT FALSE,
    ruta_pdf        VARCHAR(500),    -- ruta en S3/MinIO
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_factura_fecha ON fleet_factura (fecha_emision);

-- =============================================================================
-- MÓDULO DE PENALIZACIONES (RN-08)
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_penalizacion (
    id              SERIAL PRIMARY KEY,
    contrato_id     INTEGER         NOT NULL REFERENCES fleet_contrato(id) ON DELETE CASCADE,
    tipo            VARCHAR(50)     NOT NULL,  -- exceso_horas | zona_prohibida | daño | otro
    descripcion     TEXT            NOT NULL,
    monto           DECIMAL(12,2)   NOT NULL CHECK (monto >= 0),
    fecha           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    registrado_por_id INTEGER       REFERENCES auth_user(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_penalizacion_contrato ON fleet_penalizacion (contrato_id);

-- =============================================================================
-- MÓDULO DE MANTENIMIENTO
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_mantenimiento (
    id              SERIAL PRIMARY KEY,
    vehiculo_id     INTEGER         NOT NULL REFERENCES fleet_vehiculo(id) ON DELETE RESTRICT,
    tecnico_id      INTEGER         REFERENCES auth_user(id) ON DELETE SET NULL,

    tipo            VARCHAR(20)     NOT NULL DEFAULT 'preventivo',
                                    -- preventivo | correctivo
    descripcion     TEXT,
    fecha           DATE            NOT NULL,
    km_al_momento   DECIMAL(12,2)   NOT NULL CHECK (km_al_momento >= 0),
    costo           DECIMAL(12,2)   NOT NULL DEFAULT 0 CHECK (costo >= 0),

    -- Para mantenimiento preventivo (Template Method: calcular_proximo)
    proximo_km      DECIMAL(12,2),  -- km en que se debe hacer el siguiente
    proximo_fecha   DATE,           -- fecha estimada del siguiente mantenimiento

    estado          VARCHAR(20)     NOT NULL DEFAULT 'programado',
                                    -- programado | realizado | cancelado

    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT fleet_mant_tipo_check CHECK (
        tipo IN ('preventivo', 'correctivo')
    ),
    CONSTRAINT fleet_mant_estado_check CHECK (
        estado IN ('programado', 'realizado', 'cancelado')
    )
);

CREATE INDEX IF NOT EXISTS idx_mant_vehiculo ON fleet_mantenimiento (vehiculo_id);
CREATE INDEX IF NOT EXISTS idx_mant_estado   ON fleet_mantenimiento (estado);
CREATE INDEX IF NOT EXISTS idx_mant_fecha    ON fleet_mantenimiento (fecha);

-- =============================================================================
-- MÓDULO DE TELEMETRÍA / GPS (Sprint 3 - Versión 2)
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_telemetria (
    id              BIGSERIAL PRIMARY KEY,  -- BIGSERIAL para alto volumen
    vehiculo_id     INTEGER         NOT NULL REFERENCES fleet_vehiculo(id) ON DELETE CASCADE,
    contrato_id     INTEGER         REFERENCES fleet_contrato(id) ON DELETE SET NULL,

    latitud         DECIMAL(10,7)   NOT NULL,
    longitud        DECIMAL(10,7)   NOT NULL,
    velocidad_kmh   DECIMAL(6,2)    NOT NULL DEFAULT 0,
    km_acumulado    DECIMAL(12,2)   NOT NULL DEFAULT 0,
    timestamp       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Datos adicionales del sensor
    nivel_combustible DECIMAL(5,2),  -- porcentaje
    temperatura_motor DECIMAL(6,2),  -- grados Celsius
    raw_data        JSONB            -- datos completos del GPS sin procesar
);

-- Índice temporal para consultas de monitoreo en tiempo real
CREATE INDEX IF NOT EXISTS idx_telemetria_vehiculo_ts
    ON fleet_telemetria (vehiculo_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetria_contrato
    ON fleet_telemetria (contrato_id);
-- Particionamiento por mes recomendado para producción (alto volumen)
-- CREATE TABLE fleet_telemetria_2026_04 PARTITION OF fleet_telemetria
--     FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

-- =============================================================================
-- MÓDULO DE ALERTAS (Observer Pattern — CU-08)
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_alerta (
    id              SERIAL PRIMARY KEY,
    tipo            VARCHAR(40)     NOT NULL,
                                    -- exceso_horas | mantenimiento_proximo |
                                    -- zona_prohibida | bajo_rendimiento | falla_sensor
    vehiculo_id     INTEGER         REFERENCES fleet_vehiculo(id) ON DELETE CASCADE,
    conductor_id    INTEGER         REFERENCES fleet_conductor(id) ON DELETE SET NULL,
    contrato_id     INTEGER         REFERENCES fleet_contrato(id) ON DELETE SET NULL,

    mensaje         TEXT            NOT NULL,
    prioridad       VARCHAR(10)     NOT NULL DEFAULT 'media',
                                    -- alta | media | baja
    resuelta        BOOLEAN         NOT NULL DEFAULT FALSE,
    fecha_generacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    fecha_resolucion TIMESTAMP WITH TIME ZONE,
    resuelta_por_id  INTEGER        REFERENCES auth_user(id) ON DELETE SET NULL,

    CONSTRAINT fleet_alerta_tipo_check CHECK (
        tipo IN ('exceso_horas', 'mantenimiento_proximo', 'zona_prohibida', 'bajo_rendimiento', 'falla_sensor')
    ),
    CONSTRAINT fleet_alerta_prioridad_check CHECK (
        prioridad IN ('alta', 'media', 'baja')
    )
);

CREATE INDEX IF NOT EXISTS idx_alerta_vehiculo  ON fleet_alerta (vehiculo_id);
CREATE INDEX IF NOT EXISTS idx_alerta_resuelta  ON fleet_alerta (resuelta);
CREATE INDEX IF NOT EXISTS idx_alerta_tipo      ON fleet_alerta (tipo);
CREATE INDEX IF NOT EXISTS idx_alerta_fecha     ON fleet_alerta (fecha_generacion DESC);

-- =============================================================================
-- MÓDULO DE REPORTES (Facade Pattern — CU-07)
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_reporte (
    id              SERIAL PRIMARY KEY,
    tipo            VARCHAR(40)     NOT NULL,
                                    -- ingresos | mantenimiento | rentabilidad | horas_conductor
    parametros      JSONB           NOT NULL DEFAULT '{}',
                                    -- {"vehiculo_id": 1, "desde": "2026-01-01", "hasta": "2026-03-31"}
    resultado       JSONB,          -- resultado serializado del reporte
    generado_por_id INTEGER         REFERENCES auth_user(id) ON DELETE SET NULL,
    fecha_generacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    exportado       BOOLEAN         NOT NULL DEFAULT FALSE,
    ruta_archivo    VARCHAR(500)    -- ruta en S3/MinIO del PDF/Excel exportado
);

CREATE INDEX IF NOT EXISTS idx_reporte_tipo  ON fleet_reporte (tipo);
CREATE INDEX IF NOT EXISTS idx_reporte_fecha ON fleet_reporte (fecha_generacion DESC);

-- =============================================================================
-- AUDITORÍA (RNF-04)
-- =============================================================================

CREATE TABLE IF NOT EXISTS fleet_auditoria (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INTEGER         REFERENCES auth_user(id) ON DELETE SET NULL,
    tabla           VARCHAR(80)     NOT NULL,
    registro_id     INTEGER         NOT NULL,
    accion          VARCHAR(10)     NOT NULL,  -- INSERT | UPDATE | DELETE
    datos_antes     JSONB,
    datos_despues   JSONB,
    ip_address      INET,
    timestamp       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_tabla   ON fleet_auditoria (tabla, registro_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_user    ON fleet_auditoria (user_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_ts      ON fleet_auditoria (timestamp DESC);

-- =============================================================================
-- FUNCIÓN: actualizar updated_at automáticamente
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a tablas con updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'fleet_vehiculo',
        'fleet_conductor',
        'fleet_contrato',
        'fleet_mantenimiento',
        'fleet_perfil_usuario'
    ] LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS trg_%s_updated_at ON %s;
             CREATE TRIGGER trg_%s_updated_at
             BEFORE UPDATE ON %s
             FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();',
            t, t, t, t
        );
    END LOOP;
END;
$$;

-- =============================================================================
-- FUNCIÓN: generar número de contrato secuencial
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_numero_contrato()
RETURNS TEXT AS $$
DECLARE
    hoy     TEXT := TO_CHAR(NOW(), 'YYYYMMDD');
    seq     INTEGER;
    result  TEXT;
BEGIN
    SELECT COUNT(*) + 1 INTO seq
    FROM fleet_contrato
    WHERE numero_contrato LIKE 'CTR-' || hoy || '-%';

    result := 'CTR-' || hoy || '-' || LPAD(seq::TEXT, 4, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCIÓN: generar número de factura secuencial
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_numero_factura()
RETURNS TEXT AS $$
DECLARE
    hoy     TEXT := TO_CHAR(NOW(), 'YYYYMMDD');
    seq     INTEGER;
BEGIN
    SELECT COUNT(*) + 1 INTO seq
    FROM fleet_factura
    WHERE numero_factura LIKE 'FAC-' || hoy || '-%';

    RETURN 'FAC-' || hoy || '-' || LPAD(seq::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCIÓN: validar RN-01 (un vehículo, una renta activa) — extra seguridad
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_validar_renta_unica()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado = 'activa' THEN
        IF EXISTS (
            SELECT 1 FROM fleet_contrato
            WHERE vehiculo_id = NEW.vehiculo_id
              AND estado = 'activa'
              AND id <> NEW.id
        ) THEN
            RAISE EXCEPTION 'RN-01: El vehículo % ya tiene una renta activa.', NEW.vehiculo_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_contrato_renta_unica
BEFORE INSERT OR UPDATE ON fleet_contrato
FOR EACH ROW EXECUTE FUNCTION fn_validar_renta_unica();

-- =============================================================================
-- FUNCIÓN: actualizar km_acumulado del vehículo al cerrar contrato
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_actualizar_km_vehiculo()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo cuando el contrato pasa a 'cerrada' y km_final está definido
    IF NEW.estado = 'cerrada' AND OLD.estado = 'activa' AND NEW.km_final IS NOT NULL THEN
        UPDATE fleet_vehiculo
        SET km_acumulado = km_acumulado + (NEW.km_final - NEW.km_inicial)
        WHERE id = NEW.vehiculo_id;

        -- Liberar el vehículo (Observer Pattern: efecto secundario del cierre)
        UPDATE fleet_vehiculo
        SET estado = 'disponible'
        WHERE id = NEW.vehiculo_id AND estado = 'en_renta';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_contrato_km_vehiculo
AFTER UPDATE ON fleet_contrato
FOR EACH ROW EXECUTE FUNCTION fn_actualizar_km_vehiculo();

-- =============================================================================
-- FUNCIÓN: bloquear vehículos con mantenimiento pendiente (RN-04)
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_verificar_mantenimiento_pendiente()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado = 'activa' THEN
        IF EXISTS (
            SELECT 1 FROM fleet_mantenimiento
            WHERE vehiculo_id = NEW.vehiculo_id
              AND estado = 'programado'
        ) THEN
            RAISE EXCEPTION 'RN-04: El vehículo % tiene mantenimiento pendiente. No se puede iniciar una renta.', NEW.vehiculo_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_contrato_mant_pendiente
BEFORE INSERT ON fleet_contrato
FOR EACH ROW EXECUTE FUNCTION fn_verificar_mantenimiento_pendiente();

-- =============================================================================
-- FUNCIÓN: actualizar estado del vehículo al crear contrato
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_vehiculo_en_renta()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.estado = 'activa' THEN
        UPDATE fleet_vehiculo SET estado = 'en_renta' WHERE id = NEW.vehiculo_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_contrato_vehiculo_en_renta
AFTER INSERT ON fleet_contrato
FOR EACH ROW EXECUTE FUNCTION fn_vehiculo_en_renta();

-- =============================================================================
-- VISTAS ÚTILES PARA DJANGO ORM Y REPORTES
-- =============================================================================

-- Vista: contratos activos con datos del vehículo y conductor
CREATE OR REPLACE VIEW v_contratos_activos AS
SELECT
    c.id,
    c.numero_contrato,
    c.fecha_inicio,
    c.tipo_tarifa,
    c.tarifa_valor,
    c.km_inicial,
    v.placa,
    v.modelo,
    v.marca,
    v.km_acumulado AS km_vehiculo_actual,
    (v.km_acumulado - c.km_inicial) AS km_recorridos,
    CONCAT(d.nombre, ' ', d.apellido) AS nombre_conductor,
    d.cedula AS cedula_conductor,
    d.horas_hoy AS horas_conductor_hoy,
    d.limite_horas_dia,
    EXTRACT(EPOCH FROM (NOW() - c.fecha_inicio)) / 3600 AS horas_transcurridas
FROM fleet_contrato c
JOIN fleet_vehiculo  v ON v.id = c.vehiculo_id
JOIN fleet_conductor d ON d.id = c.conductor_id
WHERE c.estado = 'activa';

-- Vista: rentabilidad por vehículo
CREATE OR REPLACE VIEW v_rentabilidad_vehiculo AS
SELECT
    v.id AS vehiculo_id,
    v.placa,
    v.modelo,
    v.marca,
    COUNT(c.id)                         AS total_rentas,
    COALESCE(SUM(c.costo_total), 0)     AS ingresos_totales,
    COALESCE(AVG(c.costo_total), 0)     AS ingreso_promedio_renta,
    COALESCE(SUM(m.costo), 0)           AS costo_mantenimiento,
    COALESCE(SUM(c.costo_total), 0) - COALESCE(SUM(m.costo), 0) AS rentabilidad_neta,
    COALESCE(SUM(c.km_final - c.km_inicial) FILTER (WHERE c.km_final IS NOT NULL), 0) AS km_rentados
FROM fleet_vehiculo v
LEFT JOIN fleet_contrato    c ON c.vehiculo_id = v.id AND c.estado = 'cerrada'
LEFT JOIN fleet_mantenimiento m ON m.vehiculo_id = v.id AND m.estado = 'realizado'
GROUP BY v.id, v.placa, v.modelo, v.marca;

-- Vista: horas trabajadas por conductor (para RF-20)
CREATE OR REPLACE VIEW v_horas_conductor AS
SELECT
    d.id AS conductor_id,
    CONCAT(d.nombre, ' ', d.apellido) AS nombre,
    d.cedula,
    d.num_licencia,
    d.horas_hoy,
    d.horas_totales,
    d.limite_horas_dia,
    COUNT(c.id)  AS total_rentas,
    COALESCE(SUM(
        EXTRACT(EPOCH FROM (c.fecha_fin - c.fecha_inicio)) / 3600
    ) FILTER (WHERE c.fecha_fin IS NOT NULL), 0) AS horas_calculadas_contratos
FROM fleet_conductor d
LEFT JOIN fleet_contrato c ON c.conductor_id = d.id AND c.estado = 'cerrada'
GROUP BY d.id, d.nombre, d.apellido, d.cedula, d.num_licencia, d.horas_hoy, d.horas_totales, d.limite_horas_dia;

-- Vista: alertas pendientes con contexto
CREATE OR REPLACE VIEW v_alertas_pendientes AS
SELECT
    a.id,
    a.tipo,
    a.prioridad,
    a.mensaje,
    a.fecha_generacion,
    v.placa AS vehiculo_placa,
    CONCAT(d.nombre, ' ', d.apellido) AS conductor_nombre
FROM fleet_alerta a
LEFT JOIN fleet_vehiculo  v ON v.id = a.vehiculo_id
LEFT JOIN fleet_conductor d ON d.id = a.conductor_id
WHERE a.resuelta = FALSE
ORDER BY
    CASE a.prioridad WHEN 'alta' THEN 1 WHEN 'media' THEN 2 ELSE 3 END,
    a.fecha_generacion DESC;

-- =============================================================================
-- DATOS SEMILLA (fixtures equivalentes para pruebas)
-- =============================================================================

-- Vehículos de prueba
INSERT INTO fleet_vehiculo (placa, modelo, marca, anio, tipo, capacidad, color, km_inicial, km_acumulado, estado)
VALUES
    ('ABC-123', 'Corolla', 'Toyota',   2020, 'particular', 5, 'Blanco', 15000.00, 15000.00, 'disponible'),
    ('XYZ-456', 'Civic',   'Honda',    2021, 'particular', 5, 'Negro',  8000.00,  8000.00,  'disponible'),
    ('DEF-789', 'Sprinter','Mercedes', 2019, 'furgon',    12, 'Plata',  45000.00, 45000.00, 'disponible'),
    ('GHI-012', 'NHR',     'Isuzu',   2018, 'camion',     3, 'Blanco', 90000.00, 90000.00, 'mantenimiento')
ON CONFLICT (placa) DO NOTHING;

-- Conductores de prueba
INSERT INTO fleet_conductor (cedula, nombre, apellido, num_licencia, categoria_licencia, telefono, email, estado, limite_horas_dia)
VALUES
    ('1040123456', 'Carlos',  'Martínez',  'LIC-001-COL', 'B1', '3001234567', 'carlos@ope.co',  'activo', 8.00),
    ('1040654321', 'Andrés',  'Gómez',     'LIC-002-COL', 'B2', '3109876543', 'andres@ope.co',  'activo', 8.00),
    ('1040987654', 'Patricia','Herrera',   'LIC-003-COL', 'C1', '3157654321', 'patricia@ope.co','activo', 10.00)
ON CONFLICT (cedula) DO NOTHING;

-- Roles
INSERT INTO auth_rol (nombre, descripcion) VALUES
    ('admin_flota',    'Gestiona vehículos, conductores y contratos'),
    ('admin_contable', 'Accede a reportes financieros'),
    ('tecnico',        'Registra mantenimientos'),
    ('conductor',      'Consulta su renta activa')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;

-- =============================================================================
-- NOTAS DE MIGRACIÓN DJANGO
-- =============================================================================
-- Para usar este esquema con Django en lugar de generarlo desde modelos:
--
-- 1. Crear la BD:
--    createdb -U postgres ope_db
--
-- 2. Aplicar este script:
--    psql -U postgres -d ope_db -f ope_database.sql
--
-- 3. Indicarle a Django que la BD ya existe (fake migrations):
--    python manage.py migrate --fake-initial
--
-- 4. Si prefieres que Django genere las tablas desde models.py,
--    usa este archivo solo como referencia de tipos y restricciones.
--
-- Configuración en settings.py:
-- DATABASES = {
--     'default': {
--         'ENGINE': 'django.db.backends.postgresql',
--         'NAME': 'ope_db',
--         'USER': 'postgres',
--         'PASSWORD': 'tu_password',
--         'HOST': 'localhost',
--         'PORT': '5432',
--     }
-- }
-- =============================================================================
