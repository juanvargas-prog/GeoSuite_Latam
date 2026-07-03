def continuidad(mavvial,placas):
    query = """
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

    /*
    ********************************************************************************
    * Código: continuidad placas
    * Autor: Jhoinner Manrique
    * Fecha de creación: 07-07-2025
    * Última modificación: 07-07-2025
    * Versión: 1.0
    ********************************************************************************
    */

    ----------------------------------------------------------------------------------
    --crear tabla de mavvial
    drop table if exists mavvial_continuidad;
    create table mavvial_continuidad as
    select id_capa, geom, nomvtotal from  """ + mavvial + """ 
    where nomvtotal is not null or nomvtotal <> 'SN';

    alter table mavvial_continuidad add column id_buffer integer;
    alter table mavvial_continuidad add column area_buffer numeric;

    ----------------------------------------------------------------------------------
    -- crear tabla de vectores disueltos
    drop table if exists mavvial_continuidad_disuelta;
    CREATE TABLE mavvial_continuidad_disuelta AS
    SELECT
    nomvtotal,
    ST_Union(geom) AS geom
    FROM mavvial_continuidad
    GROUP BY nomvtotal;

    drop table if exists mavvial_continuidad_disuelta_buffer;
    CREATE TABLE mavvial_continuidad_disuelta_buffer AS
    SELECT
    nomvtotal,
    ST_Buffer(geom,0.000002695) AS geom
    FROM mavvial_continuidad_disuelta;

    drop table if exists mavvial_buffer;
    CREATE TABLE mavvial_buffer AS
    SELECT
    row_number() OVER () AS gid,
    nomvtotal,
    (ST_Dump(geom)).geom AS geom
    FROM mavvial_continuidad_disuelta_buffer;

    drop table mavvial_continuidad_disuelta;
    drop table mavvial_continuidad_disuelta_buffer;

    alter table mavvial_buffer add column id_buffer serial;
    alter table mavvial_buffer add column area_buffer numeric;
    create index idx_geom_buffer on mavvial_buffer using gist (geom);

    UPDATE mavvial_buffer
    SET area_buffer = ST_Area(ST_Transform(geom, 3857)); 

    ----------------------------------------------------------------------------------
    --asignar id_buffer a mavvial y area

    UPDATE mavvial_continuidad m
    SET id_buffer = b.id_buffer, area_buffer = b.area_buffer
    FROM mavvial_buffer b
    WHERE ST_Intersects(
            ST_LineInterpolatePoint(ST_LineMerge(m.geom), 0.5),
            b.geom);

    ----------------------------------------------------------------------------------
    --CREAR TABLA CON PUNTOS INICIALES
    DROP TABLE IF EXISTS start_point_mavvial;
    CREATE TABLE start_point_mavvial AS
    SELECT
        id_capa,
        nomvtotal,-- o el ID que tengas en la tabla original
        ST_StartPoint(geom) AS geom
    FROM mavvial_continuidad;

    ALTER TABLE start_point_mavvial
    ALTER COLUMN geom TYPE geometry(Point, 4326); 

    --CREAR INDICE
    drop index if exists idx_geom_start_point;
    CREATE INDEX idx_geom_start_point on start_point_mavvial using gist (geom);

    ----------------------------------------------------------------------------------
    --CREAR TABLA CON PUNTOS FINALES
    DROP TABLE IF EXISTS end_point_mavvial;
    CREATE TABLE end_point_mavvial AS
    SELECT
        id_capa,
        nomvtotal,
        ST_EndPoint(ST_LineMerge(geom)) AS geom
    FROM mavvial_continuidad;

    ALTER TABLE end_point_mavvial
    ALTER COLUMN geom TYPE geometry(Point, 4326)
    USING geom::geometry(Point, 4326); 

    ----------------------------------------------------------------------------------
    -- 1. Crear la tabla ptos_mavvial_continuidad
    DROP TABLE IF EXISTS ptos_mavvial_continuidad;

    CREATE TABLE ptos_mavvial_continuidad (
        id SERIAL PRIMARY KEY,
        id_capa INTEGER,
        nomvtotal TEXT,
        geom GEOMETRY(POINT, 4326), -- Ajusta el SRID si es diferente
        sentido TEXT
    );

    -- 2. Insertar registros desde end_point_mavvial
    INSERT INTO ptos_mavvial_continuidad (id_capa, nomvtotal, geom, sentido)
    SELECT id_capa, nomvtotal, geom, 'end_point_mavvial'
    FROM end_point_mavvial;

    -- 3. Insertar registros desde start_point_mavvial
    INSERT INTO ptos_mavvial_continuidad (id_capa, nomvtotal, geom, sentido)
    SELECT id_capa, nomvtotal, geom, 'start_point_mavvial'
    FROM start_point_mavvial;

    -- crear indice espacial
    create index idx_ptos_mavvial_continuidad on ptos_mavvial_continuidad using gist (geom);
    -- borrar capas de start y end
    drop table end_point_mavvial;
    drop table start_point_mavvial;

    -- crear campos de nomvia y id
    alter table ptos_mavvial_continuidad add column nomvia1 varchar;
    alter table ptos_mavvial_continuidad add column id_mavvial1 varchar;

    alter table ptos_mavvial_continuidad add column nomvia2 varchar;
    alter table ptos_mavvial_continuidad add column id_mavvial2 varchar;

    alter table ptos_mavvial_continuidad add column nomvia3 varchar;
    alter table ptos_mavvial_continuidad add column id_mavvial3 varchar;

    alter table ptos_mavvial_continuidad add column nomvia4 varchar;
    alter table ptos_mavvial_continuidad add column id_mavvial4 varchar;

    ----------------------------------------------------------------------------
    --fusionar los datos Actualizar los campos con datos de otros puntos que comparten geometría
    WITH relacionados AS (
        SELECT 
            p1.id AS id_base,
            array_agg(p2.nomvtotal ORDER BY p2.id) AS vias,
            array_agg(p2.id_capa ORDER BY p2.id) AS capas
        FROM ptos_mavvial_continuidad p1
        JOIN ptos_mavvial_continuidad p2
            ON ST_Equals(p1.geom, p2.geom)
        AND p1.id <> p2.id  -- Excluirse a sí mismo
        GROUP BY p1.id
    )
    UPDATE ptos_mavvial_continuidad AS base
    SET
        nomvia1 = r.vias[1],
        id_mavvial1 = r.capas[1],
        nomvia2 = r.vias[2],
        id_mavvial2 = r.capas[2],
        nomvia3 = r.vias[3],
        id_mavvial3 = r.capas[3],
        nomvia4 = r.vias[4],
        id_mavvial4 = r.capas[4]
    FROM relacionados r
    WHERE base.id = r.id_base;

    ---------------------------------------------------------------
    -- descartar registros

    delete from ptos_mavvial_continuidad
    where nomvtotal = nomvia1;

    delete from ptos_mavvial_continuidad
    where nomvtotal = nomvia2;

    delete from ptos_mavvial_continuidad
    where nomvtotal = nomvia3;

    delete from ptos_mavvial_continuidad
    where nomvtotal = nomvia4;

    delete from ptos_mavvial_continuidad
    where nomvia1 is null and nomvia2 is null and nomvia3 is null and nomvia4 is null;

    delete from ptos_mavvial_continuidad
    where (nomvia1 = nomvia2) and (nomvia3 is null and nomvia4 is null);

    -----------------------------------------------------------------------
    -- HOMOLOGAR
    -----------------------------------------------------------------------
    ----------------------------------------------------------------------------
    --Funcion de palabras a descartar
    DROP FUNCTION IF EXISTS listado_palabras();
    CREATE OR REPLACE FUNCTION listado_palabras()
    RETURNS text AS $$
    BEGIN
        RETURN '\m(ALAMEDA|ANDADOR|AUTOPISTA|AVENID PROLONGACION|AVENIDA|AVENIDA AUXILIAR|BOULEVARD|CALLE|CALLEJON|CALZADA|CAMINO|CARRETERA|CIRCUITO|CORREDOR|DIAGONAL|ESCALINATA|HERRADURA|JIRON|PASAJE|PASEO|PASEO PEATONAL|PRIVADA|PEATONAL|PROLONGACION|RETORNO|SENDERO|TRANSVERSAL)\M';
    END;
    $$ LANGUAGE plpgsql;

    ----------------------------------------------------------------------------
    --Crear campos limpios
    alter table ptos_mavvial_continuidad add column nomvia_original_limpio varchar;
    alter table ptos_mavvial_continuidad add column nomvia1_limpio varchar;
    alter table ptos_mavvial_continuidad add column nomvia2_limpio varchar;
    alter table ptos_mavvial_continuidad add column nomvia3_limpio varchar;
    alter table ptos_mavvial_continuidad add column nomvia4_limpio varchar;

    UPDATE ptos_mavvial_continuidad
    SET nomvia_original_limpio = unaccent(nomvtotal);

    UPDATE ptos_mavvial_continuidad
    SET nomvia1_limpio = unaccent(nomvia1);

    UPDATE ptos_mavvial_continuidad
    SET nomvia2_limpio = unaccent(nomvia2);

    UPDATE ptos_mavvial_continuidad
    SET nomvia3_limpio = unaccent(nomvia3);

    UPDATE ptos_mavvial_continuidad
    SET nomvia4_limpio = unaccent(nomvia4);

    -----------------------------------------------------------------------
    -- NUMEROS A TEXTO
    -----------------------------------------------------------------------
    drop table if exists conversion_numeros;
    CREATE TABLE conversion_numeros (
        numero_natural varchar,
        numero_texto VARCHAR(50) NOT NULL
    );

    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (0, 'CERO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (1, 'UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (2, 'DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (3, 'TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (4, 'CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (5, 'CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (6, 'SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (7, 'SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (8, 'OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (9, 'NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (10, 'DIEZ');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (11, 'ONCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (12, 'DOCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (13, 'TRECE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (14, 'CATORCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (15, 'QUINCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (16, 'DIECISÉIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (17, 'DIECISIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (18, 'DIECIOCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (19, 'DIECINUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (20, 'VEINTE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (21, 'VEINTIÚN');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (22, 'VEINTIDÓS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (23, 'VEINTITRÉS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (24, 'VEINTICUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (25, 'VEINTICINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (26, 'VEINTISÉIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (27, 'VEINTISIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (28, 'VEINTIOCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (29, 'VEINTINUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (30, 'TREINTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (31, 'TREINTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (32, 'TREINTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (33, 'TREINTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (34, 'TREINTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (35, 'TREINTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (36, 'TREINTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (37, 'TREINTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (38, 'TREINTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (39, 'TREINTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (40, 'CUARENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (41, 'CUARENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (42, 'CUARENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (43, 'CUARENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (44, 'CUARENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (45, 'CUARENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (46, 'CUARENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (47, 'CUARENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (48, 'CUARENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (49, 'CUARENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (50, 'CINCUENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (51, 'CINCUENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (52, 'CINCUENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (53, 'CINCUENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (54, 'CINCUENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (55, 'CINCUENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (56, 'CINCUENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (57, 'CINCUENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (58, 'CINCUENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (59, 'CINCUENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (60, 'SESENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (61, 'SESENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (62, 'SESENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (63, 'SESENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (64, 'SESENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (65, 'SESENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (66, 'SESENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (67, 'SESENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (68, 'SESENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (69, 'SESENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (70, 'SETENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (71, 'SETENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (72, 'SETENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (73, 'SETENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (74, 'SETENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (75, 'SETENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (76, 'SETENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (77, 'SETENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (78, 'SETENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (79, 'SETENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (80, 'OCHENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (81, 'OCHENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (82, 'OCHENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (83, 'OCHENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (84, 'OCHENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (85, 'OCHENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (86, 'OCHENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (87, 'OCHENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (88, 'OCHENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (89, 'OCHENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (90, 'NOVENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (91, 'NOVENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (92, 'NOVENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (93, 'NOVENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (94, 'NOVENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (95, 'NOVENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (96, 'NOVENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (97, 'NOVENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (98, 'NOVENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (99, 'NOVENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (100, 'CIEN');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (101, 'CIENTO UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (102, 'CIENTO DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (103, 'CIENTO TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (104, 'CIENTO CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (105, 'CIENTO CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (106, 'CIENTO SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (107, 'CIENTO SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (108, 'CIENTO OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (109, 'CIENTO NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (110, 'CIENTO DIEZ');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (111, 'CIENTO ONCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (112, 'CIENTO DOCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (113, 'CIENTO TRECE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (114, 'CIENTO CATORCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (115, 'CIENTO QUINCE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (116, 'CIENTO DIECISÉIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (117, 'CIENTO DIECISIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (118, 'CIENTO DIECIOCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (119, 'CIENTO DIECINUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (120, 'CIENTO VEINTE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (121, 'CIENTO VEINTIÚN');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (122, 'CIENTO VEINTIDÓS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (123, 'CIENTO VEINTITRÉS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (124, 'CIENTO VEINTICUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (125, 'CIENTO VEINTICINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (126, 'CIENTO VEINTISÉIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (127, 'CIENTO VEINTISIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (128, 'CIENTO VEINTIOCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (129, 'CIENTO VEINTINUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (130, 'CIENTO TREINTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (131, 'CIENTO TREINTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (132, 'CIENTO TREINTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (133, 'CIENTO TREINTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (134, 'CIENTO TREINTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (135, 'CIENTO TREINTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (136, 'CIENTO TREINTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (137, 'CIENTO TREINTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (138, 'CIENTO TREINTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (139, 'CIENTO TREINTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (140, 'CIENTO CUARENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (141, 'CIENTO CUARENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (142, 'CIENTO CUARENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (143, 'CIENTO CUARENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (144, 'CIENTO CUARENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (145, 'CIENTO CUARENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (146, 'CIENTO CUARENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (147, 'CIENTO CUARENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (148, 'CIENTO CUARENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (149, 'CIENTO CUARENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (150, 'CIENTO CINCUENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (151, 'CIENTO CINCUENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (152, 'CIENTO CINCUENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (153, 'CIENTO CINCUENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (154, 'CIENTO CINCUENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (155, 'CIENTO CINCUENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (156, 'CIENTO CINCUENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (157, 'CIENTO CINCUENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (158, 'CIENTO CINCUENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (159, 'CIENTO CINCUENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (160, 'CIENTO SESENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (161, 'CIENTO SESENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (162, 'CIENTO SESENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (163, 'CIENTO SESENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (164, 'CIENTO SESENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (165, 'CIENTO SESENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (166, 'CIENTO SESENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (167, 'CIENTO SESENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (168, 'CIENTO SESENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (169, 'CIENTO SESENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (170, 'CIENTO SETENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (171, 'CIENTO SETENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (172, 'CIENTO SETENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (173, 'CIENTO SETENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (174, 'CIENTO SETENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (175, 'CIENTO SETENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (176, 'CIENTO SETENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (177, 'CIENTO SETENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (178, 'CIENTO SETENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (179, 'CIENTO SETENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (180, 'CIENTO OCHENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (181, 'CIENTO OCHENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (182, 'CIENTO OCHENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (183, 'CIENTO OCHENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (184, 'CIENTO OCHENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (185, 'CIENTO OCHENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (186, 'CIENTO OCHENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (187, 'CIENTO OCHENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (188, 'CIENTO OCHENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (189, 'CIENTO OCHENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (190, 'CIENTO NOVENTA');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (191, 'CIENTO NOVENTA Y UNO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (192, 'CIENTO NOVENTA Y DOS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (193, 'CIENTO NOVENTA Y TRES');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (194, 'CIENTO NOVENTA Y CUATRO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (195, 'CIENTO NOVENTA Y CINCO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (196, 'CIENTO NOVENTA Y SEIS');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (197, 'CIENTO NOVENTA Y SIETE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (198, 'CIENTO NOVENTA Y OCHO');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (199, 'CIENTO NOVENTA Y NUEVE');
    INSERT INTO conversion_numeros (numero_natural, numero_texto) VALUES (200, 'DOSCIENTOS');

    alter table conversion_numeros drop column if exists numero_homologado;
    alter table conversion_numeros add column numero_homologado varchar;

    update conversion_numeros
    set numero_homologado = unaccent(replace(numero_texto,' ',''));

    create index idx_numeronatural on conversion_numeros(numero_natural);
    create index idx_numerotexto on conversion_numeros(numero_texto);

    -----------------------------------------------------------------------
    --natural a texto en nomvia_placas

    UPDATE ptos_mavvial_continuidad c
    SET nomvia_original_limpio = regexp_replace(
    c.nomvia_original_limpio,
    '\m' || cn.numero_natural || '\M',
    cn.numero_homologado,
    'gi'
    )
    FROM conversion_numeros cn
    WHERE c.nomvia_original_limpio ~ ('\m' || cn.numero_natural || '\M');

    -----------------------------------------------------------------------
    --natural a texto en nomvia1

    UPDATE ptos_mavvial_continuidad c
    SET nomvia1_limpio = regexp_replace(
    c.nomvia1_limpio,
    '\m' || cn.numero_natural || '\M',
    cn.numero_homologado,
    'gi'
    )
    FROM conversion_numeros cn
    WHERE c.nomvia1_limpio ~ ('\m' || cn.numero_natural || '\M');

    -----------------------------------------------------------------------
    --natural a texto en nomvia2

    UPDATE ptos_mavvial_continuidad c
    SET nomvia2_limpio = regexp_replace(
    c.nomvia2_limpio,
    '\m' || cn.numero_natural || '\M',
    cn.numero_homologado,
    'gi'
    )
    FROM conversion_numeros cn
    WHERE c.nomvia2_limpio ~ ('\m' || cn.numero_natural || '\M');

    -----------------------------------------------------------------------
    --natural a texto en nomvia3

    UPDATE ptos_mavvial_continuidad c
    SET nomvia3_limpio = regexp_replace(
    c.nomvia3_limpio,
    '\m' || cn.numero_natural || '\M',
    cn.numero_homologado,
    'gi'
    )
    FROM conversion_numeros cn
    WHERE c.nomvia3_limpio ~ ('\m' || cn.numero_natural || '\M');

    -----------------------------------------------------------------------
    --natural a texto en nomvia4

    UPDATE ptos_mavvial_continuidad c
    SET nomvia4_limpio = regexp_replace(
    c.nomvia4_limpio,
    '\m' || cn.numero_natural || '\M',
    cn.numero_homologado,
    'gi'
    )
    FROM conversion_numeros cn
    WHERE c.nomvia4_limpio ~ ('\m' || cn.numero_natural || '\M');

    -------------------------------------------------------------------------
    --Quitar palabras irrelevantes
    -------------------------------------------------------------------------

    --nomvia_placas
    UPDATE ptos_mavvial_continuidad
    SET 
        nomvia_original_limpio = REGEXP_REPLACE(nomvia_original_limpio, listado_palabras(), '', 'g')
    WHERE
        nomvia_original_limpio is not null and nomvia_original_limpio ~ listado_palabras();
        
    --dobles espacios	
    UPDATE ptos_mavvial_continuidad
    SET nomvia_original_limpio = regexp_replace(trim(nomvia_original_limpio), '\s+', ' ', 'g');

    ---------------------------------------------------------------------------
    --nomvia1_limpio
    UPDATE ptos_mavvial_continuidad
    SET 
        nomvia1_limpio = REGEXP_REPLACE(nomvia1_limpio, listado_palabras(), '', 'g')
    WHERE
        nomvia1_limpio is not null and nomvia1_limpio ~ listado_palabras();
        
    --dobles espacios	
    UPDATE ptos_mavvial_continuidad
    SET nomvia1_limpio = regexp_replace(trim(nomvia1_limpio), '\s+', ' ', 'g');
    ----------------------------------------------------------------------------
    --nomvia2_limpio
    UPDATE ptos_mavvial_continuidad
    SET 
        nomvia2_limpio = REGEXP_REPLACE(nomvia2_limpio, listado_palabras(), '', 'g')
    WHERE
        nomvia2_limpio is not null and nomvia2_limpio ~ listado_palabras();
        
    --dobles espacios	
    UPDATE ptos_mavvial_continuidad
    SET nomvia2_limpio = regexp_replace(trim(nomvia2_limpio), '\s+', ' ', 'g');

    ----------------------------------------------------------------------------
    --nomvia3_limpio
    UPDATE ptos_mavvial_continuidad
    SET 
        nomvia3_limpio = REGEXP_REPLACE(nomvia3_limpio, listado_palabras(), '', 'g')
    WHERE
        nomvia3_limpio is not null and nomvia3_limpio ~ listado_palabras();
        
    --dobles espacios	
    UPDATE ptos_mavvial_continuidad
    SET nomvia3_limpio = regexp_replace(trim(nomvia3_limpio), '\s+', ' ', 'g');

    ----------------------------------------------------------------------------
    --nomvia4_limpio
    UPDATE ptos_mavvial_continuidad
    SET 
        nomvia4_limpio = REGEXP_REPLACE(nomvia4_limpio, listado_palabras(), '', 'g')
    WHERE
        nomvia4_limpio is not null and nomvia4_limpio ~ listado_palabras();
        
    --dobles espacios	
    UPDATE ptos_mavvial_continuidad
    SET nomvia4_limpio = regexp_replace(trim(nomvia4_limpio), '\s+', ' ', 'g');


    -----------------------------------------------------------------------
    ----------------------- COMPARACIONES ---------------------------------
    -----------------------------------------------------------------------
    do $$
    begin
        raise notice 'Iniciando Metodo Directo...';
    End $$;
    BEGIN;
    -----------------------------------------------------------------------
    -- Metodo directo
    -----------------------------------------------------------------------

    -- columna nom_directo existe
    ALTER TABLE ptos_mavvial_continuidad DROP COLUMN IF EXISTS nom_directo;
    ALTER TABLE ptos_mavvial_continuidad ADD COLUMN nom_directo TEXT;

    -- Paso 1: comparar con nomvia1_limpio
    UPDATE ptos_mavvial_continuidad
    SET nom_directo = nomvia1
    WHERE nom_directo IS NULL
    AND nomvia_original_limpio = nomvia1_limpio;

    -- Paso 2: comparar con nomvia2_limpio
    UPDATE ptos_mavvial_continuidad
    SET nom_directo = nomvia2
    WHERE nom_directo IS NULL
    AND nomvia_original_limpio = nomvia2_limpio;

    -- Paso 3: comparar con nomvia3_limpio
    UPDATE ptos_mavvial_continuidad
    SET nom_directo = nomvia3
    WHERE nom_directo IS NULL
    AND nomvia_original_limpio = nomvia3_limpio;

    -- Paso 4: comparar con nomvia4_limpio
    UPDATE ptos_mavvial_continuidad
    SET nom_directo = nomvia4
    WHERE nom_directo IS NULL
    AND nomvia_original_limpio = nomvia4_limpio;
    
    do $$
    begin
        raise notice 'Metodo Directo, 50%%...';
    end $$;

    commit;

    -----------------------------------------------------------------------
    -- Metodo Similarity
    -----------------------------------------------------------------------
    begin;

    do $$
    begin
        raise notice 'Iniciando metodo Similarity...';
    end $$;

    --Se asigna el nom_homologado para los directo, para descartarlos en los demas pasos.

    ALTER TABLE ptos_mavvial_continuidad drop COLUMN if exists id_mavvial;
    ALTER TABLE ptos_mavvial_continuidad ADD COLUMN id_mavvial varchar;

    ALTER TABLE ptos_mavvial_continuidad drop COLUMN if exists nom_homologado;
    ALTER TABLE ptos_mavvial_continuidad ADD COLUMN nom_homologado TEXT;

    ALTER TABLE ptos_mavvial_continuidad drop COLUMN if exists tipo_homologacion;
    ALTER TABLE ptos_mavvial_continuidad ADD COLUMN tipo_homologacion varchar;

    --Placa por homologacion exacta
    UPDATE ptos_mavvial_continuidad 
    SET 
        nom_homologado = nom_directo,
        tipo_homologacion = 'directo'
    WHERE 
        nom_directo IS NOT NULL;

    -- Asignar id_mavvial directo
    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial1
    where nom_homologado = nomvia1 and id_mavvial is null;

    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial2
    where nom_homologado = nomvia2 and id_mavvial is null;

    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial3
    where nom_homologado = nomvia3 and id_mavvial is null;

    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial4
    where nom_homologado = nomvia4 and id_mavvial is null;


    --Primero se limpian aquellos registros que al quitar las palabras irrelevantes
    --deja como remanente una letra independiente o dos letras, con el fin de evitar falsos positivos
    update ptos_mavvial_continuidad
    set nomvia1_limpio = null, nomvia1 = null
    WHERE (length(REGEXP_REPLACE(nomvia1_limpio, '\s', '', 'g')) <= 2
    AND REGEXP_REPLACE(nomvia1_limpio, '\s', '', 'g') ~ '^[A-Za-z]+$') or nomvia1_limpio is null;

    UPDATE ptos_mavvial_continuidad
    SET nomvia1_limpio = NULL, nomvia1 = NULL
    WHERE nomvia1_limpio IN (
    'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 
    'SEIS', 'SIETE', 'OCHO', 'NUEVE', 'DIEZ', 'CERO'
    );
    
    update ptos_mavvial_continuidad
    set nomvia2_limpio = null, nomvia2 = null
    WHERE (length(REGEXP_REPLACE(nomvia2_limpio, '\s', '', 'g')) <= 2
    AND REGEXP_REPLACE(nomvia2_limpio, '\s', '', 'g') ~ '^[A-Za-z]+$') or nomvia2_limpio is null;
    
    UPDATE ptos_mavvial_continuidad
    SET nomvia2_limpio = NULL, nomvia2 = NULL
    WHERE nomvia2_limpio IN (
    'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 
    'SEIS', 'SIETE', 'OCHO', 'NUEVE', 'DIEZ', 'CERO'
    );  
    
    update ptos_mavvial_continuidad
    set nomvia3_limpio = null, nomvia3 = null
    WHERE (length(REGEXP_REPLACE(nomvia3_limpio, '\s', '', 'g')) <= 2
    AND REGEXP_REPLACE(nomvia3_limpio, '\s', '', 'g') ~ '^[A-Za-z]+$') or nomvia3_limpio is null;
    
    UPDATE ptos_mavvial_continuidad
    SET nomvia3_limpio = NULL, nomvia3 = NULL
    WHERE nomvia3_limpio IN (
    'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 
    'SEIS', 'SIETE', 'OCHO', 'NUEVE', 'DIEZ', 'CERO'
    );

    update ptos_mavvial_continuidad
    set nomvia4_limpio = null, nomvia4 = null
    WHERE (length(REGEXP_REPLACE(nomvia4_limpio, '\s', '', 'g')) <= 2
    AND REGEXP_REPLACE(nomvia4_limpio, '\s', '', 'g') ~ '^[A-Za-z]+$') or nomvia4_limpio is null;
    
    UPDATE ptos_mavvial_continuidad
    SET nomvia4_limpio = NULL, nomvia4 = NULL
    WHERE nomvia4_limpio IN (
    'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 
    'SEIS', 'SIETE', 'OCHO', 'NUEVE', 'DIEZ', 'CERO'
    );
    
    commit;

    -----------------------------------------------------------------------
    --Similarity placas en mavvial

    begin;

    ALTER TABLE ptos_mavvial_continuidad drop COLUMN if exists nom_similarity;
    ALTER TABLE ptos_mavvial_continuidad ADD COLUMN nom_similarity TEXT;

    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, SIMILARITY(nomvtotal, COALESCE(nomvia1, ''))),
                        (nomvia2, SIMILARITY(nomvtotal, COALESCE(nomvia2, ''))),
                        (nomvia3, SIMILARITY(nomvtotal, COALESCE(nomvia3, ''))),
                        (nomvia4, SIMILARITY(nomvtotal, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.7  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL;
    commit;

    do $$
    begin
        raise notice 'Metodo Similarity, 20%%...';
    end $$;

    -----------------------------------------------------------------------
    --Similarity placas en mavvial_limpio

    begin;
    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.7  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_similarity is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity, 40%%...';
    end $$;

    -----------------------------------------------------------------------
    --Similarity placas_limpio en mavvial

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia1, ''))),
                        (nomvia2, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia2, ''))),
                        (nomvia3, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia3, ''))),
                        (nomvia4, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.7  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    and ptos_mavvial_continuidad.nom_similarity is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity, 60%%...';
    end $$;

    -----------------------------------------------------------------------
    --Similarity placas_limpio en mavvial_limpio

    begin;


    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.7  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_similarity is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity, 80%%...';
    end $$;

    -----------------------------------------------------------------------
    --Asignar nombres sin limpiar
    -----------------------------------------------------------------------
    begin;

    update ptos_mavvial_continuidad
    set nom_similarity = nomvia1
    where nom_similarity = nomvia1_limpio
    and nom_similarity is not null;

    update ptos_mavvial_continuidad
    set nom_similarity = nomvia2
    where nom_similarity = nomvia2_limpio
    and nom_similarity is not null;

    update ptos_mavvial_continuidad
    set nom_similarity = nomvia3
    where nom_similarity = nomvia3_limpio
    and nom_similarity is not null;
    commit; 

    do $$
    begin
        raise notice 'Metodo Similarity, finalizado...';
    end $$;

    ANALYZE ptos_mavvial_continuidad;
    -----------------------------------------------------------------------
    -- comparar variaciones con levenshtein
    -----------------------------------------------------------------------
    begin;

    do $$
    begin
        raise notice 'Iniciando metodo Levenshtein...';
    end $$;
    -----------------------------------------------------------------------
    --LEVENSHTEIN placas en mavvial
    ALTER TABLE ptos_mavvial_continuidad drop COLUMN if exists nom_levenshtein;
    ALTER TABLE ptos_mavvial_continuidad ADD COLUMN nom_levenshtein TEXT;

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, LEVENSHTEIN(nomvtotal, COALESCE(nomvia1, ''))),
                        (nomvia2, LEVENSHTEIN(nomvtotal, COALESCE(nomvia2, ''))),
                        (nomvia3, LEVENSHTEIN(nomvtotal, COALESCE(nomvia3, ''))),
                        (nomvia4, LEVENSHTEIN(nomvtotal, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 5  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein, 20%%...';
    end $$;

    -----------------------------------------------------------------------
    --LEVENSHTEIN placas en mavvial_limpio

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 5  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
        and ptos_mavvial_continuidad.nom_levenshtein is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein, 40%%...';
    end $$;


    -----------------------------------------------------------------------
    --levenshtein placas_limpio en mavvial

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia1, ''))),
                        (nomvia2, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia2, ''))),
                        (nomvia3, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia3, ''))),
                        (nomvia4, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 5  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
        and ptos_mavvial_continuidad.nom_levenshtein is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    and ptos_mavvial_continuidad.nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein, 60%%...';
    end $$;


    -----------------------------------------------------------------------
    --levenshtein placas_limpio en mavvial_limpio

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 5  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
        and ptos_mavvial_continuidad.nom_levenshtein is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    and ptos_mavvial_continuidad.nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein, 80%%...';
    end $$;


    -----------------------------------------------------------------------
    --Asignar nombres sin limpiar
    -----------------------------------------------------------------------

    update ptos_mavvial_continuidad
    set nom_levenshtein = nomvia1
    where nom_levenshtein = nomvia1_limpio
    and nom_levenshtein is not null;

    update ptos_mavvial_continuidad
    set nom_levenshtein = nomvia2
    where nom_levenshtein = nomvia2_limpio
    and nom_levenshtein is not null;

    update ptos_mavvial_continuidad
    set nom_levenshtein = nomvia3
    where nom_levenshtein = nomvia3_limpio
    and nom_levenshtein is not null;
    --------------------------------------------------


    do $$
    begin
        raise notice 'Metodo Levenshtein, Finalizado...';
    end $$;

    ANALYZE ptos_mavvial_continuidad;
    -----------------------------------------------------------------------
    --LIMPIAR RESULTADOS DISTINTOS EN SIMILARITY Y LEVENSHTEIN
    -----------------------------------------------------------------------

    UPDATE ptos_mavvial_continuidad
    set nom_similarity = null, nom_levenshtein = null
    where nom_similarity <> nom_levenshtein and nom_directo is null;

    UPDATE ptos_mavvial_continuidad
    set nom_similarity = null, nom_levenshtein = null
    where (nom_similarity is null or nom_levenshtein is null)and nom_directo is null;

    -----------------------------------------------------------------------
    --METODO XWORD
    -----------------------------------------------------------------------
    begin;
    do $$
    begin
        raise notice 'Iniciando metodo Xword...';
    end $$;
    --------------------------------------------------
    ALTER TABLE ptos_mavvial_continuidad DROP COLUMN IF EXISTS nom_xword;
    ALTER TABLE ptos_mavvial_continuidad ADD COLUMN nom_xword VARCHAR;

    -----------------------------------------------------------------------
    --placas en mavvial
    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia1
    where nomvia1 ~ ('\m' || nomvtotal || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia2
    where nomvia2 ~ ('\m' || nomvtotal || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia3
    where nomvia3 ~ ('\m' || nomvtotal || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Xword, 10%%...';
    end $$;


    -----------------------------------------------------------------------
    --mavvial en placas

    begin;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia1
    where nomvtotal ~ ('\m' || nomvia1 || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia2
    where nomvtotal ~ ('\m' || nomvia2 || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia3
    where nomvtotal ~ ('\m' || nomvia3 || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Xword, 20%%...';
    end $$;


    -----------------------------------------------------------------------
    --placas_limpio en mavvial

    begin;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia1
    where nomvia1 ~ ('\m' || nomvia_original_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia2
    where nomvia2 ~ ('\m' || nomvia_original_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia3
    where nomvia3 ~ ('\m' || nomvia_original_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Xword, 30%%...';
    end $$;


    -----------------------------------------------------------------------
    --placas_limpio en mavvial_limpio

    begin;


    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia1
    where nomvia1_limpio ~ ('\m' || nomvia_original_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia2
    where nomvia2_limpio ~ ('\m' || nomvia_original_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia3
    where nomvia3_limpio ~ ('\m' || nomvia_original_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Xword, 60%%...';
    end $$;


    -----------------------------------------------------------------------
    --mavvial_limpio en placas

    begin;


    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia1
    where nomvtotal ~ ('\m' || nomvia1_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia2
    where nomvtotal ~ ('\m' || nomvia2_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia3
    where nomvtotal ~ ('\m' || nomvia3_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Xword, 80%%...';
    end $$;

    -----------------------------------------------------------------------
    -- mavvial_limpio en placas_limpio

    begin;


    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia1
    where  nomvia_original_limpio ~ ('\m' || nomvia1_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia2
    where  nomvia_original_limpio ~ ('\m' || nomvia2_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    UPDATE ptos_mavvial_continuidad
    SET nom_xword = nomvia3
    where  nomvia_original_limpio ~ ('\m' || nomvia3_limpio || '\M') and nom_xword is null and nom_directo is null and nom_levenshtein is null;

    --------------------------------------------------
    commit;

    do $$
    begin
        raise notice 'Metodo Xword Finalizado...';
    end $$;


    -----------------------------------------------------------------------
    --METODO SIMILARITY MAS ESTRICTO
    -----------------------------------------------------------------------
    Begin;

    do $$
    begin
        raise notice 'Iniciando metodo Similarity Estricto...';
    end $$;
    -----------------------------------------------------------------------
    --Similarity placas en mavvial

    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, SIMILARITY(nomvtotal, COALESCE(nomvia1, ''))),
                        (nomvia2, SIMILARITY(nomvtotal, COALESCE(nomvia2, ''))),
                        (nomvia3, SIMILARITY(nomvtotal, COALESCE(nomvia3, ''))),
                        (nomvia4, SIMILARITY(nomvtotal, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.85  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null 
        and nom_similarity is null
        and nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_similarity is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity Estricto, 20%%...';
    end $$;


    -----------------------------------------------------------------------
    --Similarity placas en mavvial_limpio

    begin;


    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, SIMILARITY(nomvtotal, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.85  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null 
        and nom_similarity is null
        and nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_similarity is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity Estricto, 40%%...';
    end $$;


    -----------------------------------------------------------------------
    --Similarity placas_limpio en mavvial

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia1, ''))),
                        (nomvia2, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia2, ''))),
                        (nomvia3, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia3, ''))),
                        (nomvia4, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.85  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null 
        and nom_similarity is null
        and nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    and ptos_mavvial_continuidad.nom_similarity is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity Estricto, 60%%...';
    end $$;


    -----------------------------------------------------------------------
    --Similarity placas_limpio en mavvial_limpio

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_similarity = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, SIMILARITY(nomvia_original_limpio, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, similitud)
                WHERE similitud >= 0.85  -- Ajusta el umbral de similitud
                ORDER BY similitud DESC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where nom_directo is null 
        and nom_similarity is null
        and nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_similarity is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity Estricto, 80%%...';
    end $$;


    -----------------------------------------------------------------------
    --Asignar nombres sin limpiar
    -----------------------------------------------------------------------
    begin;

    update ptos_mavvial_continuidad
    set nom_similarity = nomvia1
    where nom_similarity = nomvia1_limpio
    and nom_similarity is not null;

    update ptos_mavvial_continuidad
    set nom_similarity = nomvia2
    where nom_similarity = nomvia2_limpio
    and nom_similarity is not null;

    update ptos_mavvial_continuidad
    set nom_similarity = nomvia3
    where nom_similarity = nomvia3_limpio
    and nom_similarity is not null;

    commit;

    do $$
    begin
        raise notice 'Metodo Similarity restrigido, Finalizado...';
    end $$;

    -----------------------------------------------------------------------
    --METODO LEVENSHTEIN MAS ESTRICTO
    -----------------------------------------------------------------------
    Begin;

    do $$
    begin
        raise notice 'Iniciando Levenshtein Estricto...';
    end $$;
    -----------------------------------------------------------------------
    --LEVENSHTEIN placas en mavvial

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, LEVENSHTEIN(nomvtotal, COALESCE(nomvia1, ''))),
                        (nomvia2, LEVENSHTEIN(nomvtotal, COALESCE(nomvia2, ''))),
                        (nomvia3, LEVENSHTEIN(nomvtotal, COALESCE(nomvia3, ''))),
                        (nomvia4, LEVENSHTEIN(nomvtotal, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 1  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
        AND ptos_mavvial_continuidad.nom_levenshtein is null
        and ptos_mavvial_continuidad.nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_levenshtein is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein Estricto, 20%%...';
    end $$;

    -----------------------------------------------------------------------
    --LEVENSHTEIN placas en mavvial_limpio

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvtotal,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, LEVENSHTEIN(nomvtotal, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 1  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
        and ptos_mavvial_continuidad.nom_levenshtein is null
        and ptos_mavvial_continuidad.nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    AND ptos_mavvial_continuidad.nom_levenshtein is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein Estricto, 40%%...';
    end $$;

    -----------------------------------------------------------------------
    --levenshtein placas_limpio en mavvial

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia1, ''))),
                        (nomvia2, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia2, ''))),
                        (nomvia3, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia3, ''))),
                        (nomvia4, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia4, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 1  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
        and ptos_mavvial_continuidad.nom_levenshtein is null
        and ptos_mavvial_continuidad.nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    and ptos_mavvial_continuidad.nom_levenshtein is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein Estricto, 60%%...';
    end $$;

    -----------------------------------------------------------------------
    --levenshtein placas_limpio en mavvial_limpio

    begin;

    UPDATE ptos_mavvial_continuidad 
    SET nom_levenshtein = subquery.nomvia_mavvial_mas_similar
    FROM (
        SELECT id_capa, nomvia_original_limpio,
            (SELECT nomvia_mavvial
                FROM (VALUES 
                        (nomvia1_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia1_limpio, ''))),
                        (nomvia2_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia2_limpio, ''))),
                        (nomvia3_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia3_limpio, ''))),
                        (nomvia4_limpio, LEVENSHTEIN(nomvia_original_limpio, COALESCE(nomvia4_limpio, '')))
                    ) AS temp(nomvia_mavvial, distancia)
                WHERE distancia <= 1  -- Ajusta el umbral de distancia de edición
                ORDER BY distancia ASC
                LIMIT 1
            ) AS nomvia_mavvial_mas_similar
        FROM ptos_mavvial_continuidad
        where ptos_mavvial_continuidad.nom_directo IS NULL
        and ptos_mavvial_continuidad.nom_levenshtein is null
        and ptos_mavvial_continuidad.nom_xword is null
    ) AS subquery
    WHERE ptos_mavvial_continuidad.id_capa = subquery.id_capa
    AND ptos_mavvial_continuidad.nom_directo IS NULL
    and ptos_mavvial_continuidad.nom_levenshtein is null
    and ptos_mavvial_continuidad.nom_xword is null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein Estricto, 80%%...';
    end $$;

    -----------------------------------------------------------------------
    --Asignar nombres sin limpiar
    -----------------------------------------------------------------------

    begin;

    update ptos_mavvial_continuidad
    set nom_levenshtein = nomvia1
    where nom_levenshtein = nomvia1_limpio
    and nom_levenshtein is not null;

    update ptos_mavvial_continuidad
    set nom_levenshtein = nomvia2
    where nom_levenshtein = nomvia2_limpio
    and nom_levenshtein is not null;

    update ptos_mavvial_continuidad
    set nom_levenshtein = nomvia3
    where nom_levenshtein = nomvia3_limpio
    and nom_levenshtein is not null;

    commit;

    do $$
    begin
        raise notice 'Metodo Levenshtein restringido, Finalizado...';
    End $$;

    ----------------------------------------------------------------------
    -------------------- elegir nom_final Y id_final----------------------
    ----------------------------------------------------------------------
    do $$
    begin
        raise notice 'Asignando nombre homologado...';
    End $$;
        
    --doble cuando Coincidencias exactas entre similarity Y levenshtein
    UPDATE ptos_mavvial_continuidad 
    SET 
        nom_homologado = nom_similarity,
        tipo_homologacion = 'doble'
    WHERE 
        nom_similarity IS NOT NULL 
        AND nom_levenshtein IS NOT NULL
        AND nom_similarity = nom_levenshtein
        and nom_homologado is null;
        
    -- similarity donde nom_final sigue siendo NULL
    UPDATE ptos_mavvial_continuidad 
    SET 
        nom_homologado = nom_similarity,
        tipo_homologacion = 'simple_similarity'
    WHERE 
        nom_homologado IS NULL 
        AND nom_similarity IS NOT NULL;
        
    -- xword donde nom_final sigue siendo NULL
    UPDATE ptos_mavvial_continuidad 
    SET 
        nom_homologado = nom_xword,
        tipo_homologacion = 'simple_xword'
    WHERE 
        nom_homologado IS NULL 
        AND nom_xword IS NOT NULL;
        
    -- Levenshtein donde nom_final sigue siendo NULL
    UPDATE ptos_mavvial_continuidad 
    SET 
        nom_homologado = nom_levenshtein,
        tipo_homologacion = 'simple_levenshtein'
    WHERE 
        nom_homologado IS NULL 
        and nom_levenshtein is not null;

    -- Sin homologar donde nom_final sigue siendo NULL
    update ptos_mavvial_continuidad
    set tipo_homologacion = 'sin homologar'
    where nom_homologado is null;

    do $$
    begin
        raise notice 'Asignando id_mavvial correspondiente...';
    End $$;

    -- Asignar id_mavvial	
    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial1
    where nom_homologado = nomvia1 and id_mavvial is null;

    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial2
    where nom_homologado = nomvia2 and id_mavvial is null;

    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial3
    where nom_homologado = nomvia3 and id_mavvial is null;

    UPDATE ptos_mavvial_continuidad
    SET id_mavvial = id_mavvial4
    where nom_homologado = nomvia4 and id_mavvial is null;

    ----------------------------------------------------------------------
    ---------------------LIMPIAR CAMPOS DE PROCESOS-----------------------
    ----------------------------------------------------------------------
    alter table ptos_mavvial_continuidad drop column if exists id_mavvial1;
    alter table ptos_mavvial_continuidad drop column if exists id_mavvial2;
    alter table ptos_mavvial_continuidad drop column if exists id_mavvial3;
    alter table ptos_mavvial_continuidad drop column if exists id_mavvial4;

    alter table ptos_mavvial_continuidad drop column if exists nom_directo;
    alter table ptos_mavvial_continuidad drop column if exists nom_levenshtein;
    alter table ptos_mavvial_continuidad drop column if exists nom_similarity;
    alter table ptos_mavvial_continuidad drop column if exists nom_xword;

    drop table conversion_numeros;

    ----------------------------------------------------------------------
    ----------------------ASIGNAR NOMVIA AJUSTADO-------------------------
    ----------------------------------------------------------------------

    --eliminar los no homologados
    delete from ptos_mavvial_continuidad 
    where tipo_homologacion ='sin homologar' or id_mavvial is null;

    --asignar area propia y area de homologar
    alter table ptos_mavvial_continuidad add column area_propia numeric;
    alter table ptos_mavvial_continuidad add column area_homologacion numeric;

    update ptos_mavvial_continuidad p
    set area_propia = m.area_buffer
    from mavvial_continuidad m
    where p.id_capa = m.id_capa;

    update ptos_mavvial_continuidad p
    set area_homologacion = m.area_buffer
    from mavvial_continuidad m
    where p.id_mavvial::integer = m.id_capa;

    delete from ptos_mavvial_continuidad
    where area_propia>area_homologacion;

    -------------------------------------------------------------------
    --calcular angulo del punto
    -------------------------------------------------------------------

    alter table ptos_mavvial_continuidad add column angulo numeric;

    UPDATE ptos_mavvial_continuidad p
    SET angulo = degrees(
    acos(
        LEAST(1, GREATEST(-1,
        (
            (ST_X(ST_PointN(sub.vector1, 2)) - ST_X(sub.nodo)) * (ST_X(ST_PointN(sub.vector2, 2)) - ST_X(sub.nodo)) +
            (ST_Y(ST_PointN(sub.vector1, 2)) - ST_Y(sub.nodo)) * (ST_Y(ST_PointN(sub.vector2, 2)) - ST_Y(sub.nodo))
        ) /
        (
            ST_Distance(sub.nodo, ST_PointN(sub.vector1, 2)) * ST_Distance(sub.nodo, ST_PointN(sub.vector2, 2))
        )
        ))
    )
    )
    FROM (
    SELECT 
        p.id_capa,

        ST_Transform(p.geom, 32718) AS nodo,

        ST_MakeLine(
        ST_Transform(p.geom, 32718),
        ST_LineInterpolatePoint(
            ST_LineMerge(ST_Transform(m1.geom, 32718)),
            LEAST(1, GREATEST(0,
            ST_LineLocatePoint(ST_LineMerge(ST_Transform(m1.geom, 32718)), ST_Transform(p.geom, 32718)) +
            CASE 
                WHEN ST_LineLocatePoint(ST_LineMerge(ST_Transform(m1.geom, 32718)), ST_Transform(p.geom, 32718)) >= 0.95 THEN -0.01
                ELSE 0.01
            END
            ))
        )
        ) AS vector1,

        ST_MakeLine(
        ST_Transform(p.geom, 32718),
        ST_LineInterpolatePoint(
            ST_LineMerge(ST_Transform(m2.geom, 32718)),
            LEAST(1, GREATEST(0,
            ST_LineLocatePoint(ST_LineMerge(ST_Transform(m2.geom, 32718)), ST_Transform(p.geom, 32718)) +
            CASE 
                WHEN ST_LineLocatePoint(ST_LineMerge(ST_Transform(m2.geom, 32718)), ST_Transform(p.geom, 32718)) >= 0.95 THEN -0.01
                ELSE 0.01
            END
            ))
        )
        ) AS vector2

    FROM ptos_mavvial_continuidad p
    JOIN mavvial_continuidad m1 ON m1.id_capa = p.id_capa
    JOIN mavvial_continuidad m2 ON m2.id_capa = p.id_mavvial::integer

    ) sub
    WHERE p.id_capa = sub.id_capa
    AND ST_Distance(sub.nodo, ST_PointN(sub.vector1, 2)) > 0
    AND ST_Distance(sub.nodo, ST_PointN(sub.vector2, 2)) > 0;
    
    ---------------------------------------------------------------------------------
    --eliminar angulos inferiores a 130

    delete from ptos_mavvial_continuidad
    where angulo <= 140;

    alter table mavvial_continuidad add column id_capa_homologado integer;

    --actualizar id_homologado en mavvial
    update mavvial_continuidad m
    set id_capa_homologado = p.id_mavvial::integer
    from ptos_mavvial_continuidad p
    where m.id_capa = p.id_capa;

    --actualizar id_homologado en todo el tramo
    UPDATE mavvial_continuidad m
    SET id_capa_homologado = sub.id_capa_homologado
    FROM (
    SELECT id_buffer, MAX(id_capa_homologado) AS id_capa_homologado
    FROM mavvial_continuidad
    WHERE id_capa_homologado IS NOT NULL
    GROUP BY id_buffer
    ) sub
    WHERE m.id_buffer = sub.id_buffer
    AND m.id_capa_homologado IS NULL;
    
    --Actualizar en mavvial 
    alter table  """ + mavvial + """ add column if not exists nom_original_continuidad varchar;
    alter table  """ + mavvial + """ add column if not exists id_homologado_continuidad integer;

    update  """ + mavvial + """ m
    set id_homologado_continuidad = c.id_capa_homologado
    from mavvial_continuidad c
    where m.id_capa = c.id_capa;

    update  """ + mavvial + """ m
    set nom_original_continuidad = nomvtotal
    where id_homologado_continuidad is not null;

    update  """ + mavvial + """ p
    set tipovia = b.tipovia, nomvia=b.nomvia, nomvtotal=b.nomvtotal
    from  """ + mavvial + """ b
    where p.id_homologado_continuidad = b.id_capa;

    alter table  """ + mavvial + """ add column if not exists accion_continuidad varchar;

    update  """ + mavvial + """ p
    set accion_continuidad = 'CAMBIO_NOMVIA'
    where id_homologado_continuidad is not null;

    alter table  """ + mavvial + """ drop column id_homologado_continuidad;
        """
    print(query)
    return query
    