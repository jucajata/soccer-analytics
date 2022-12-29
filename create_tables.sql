CREATE TABLE RESULTADOS_PARTIDOS (
    FECHA DATE NOT NULL,
    EQUIPO_LOCAL VARCHAR(100) NOT NULL,
    RESULTADO_LOCAL INTEGER,
    RESULTADO_VISITANTE INTEGER,
    EQUIPO_VISITANTE VARCHAR(100) NOT NULL,
    ESTADIO VARCHAR(100) NOT NULL,
    ARBITRO VARCHAR(100) NOT NULL,
    LINK_DATOS_PARTIDO VARCHAR(100),
    COMPETICION VARCHAR(100) NOT NULL,
    PRIMARY KEY(LINK_DATOS_PARTIDO)
);


CREATE TABLE SOLICITUDES_REPORTE (
    FECHA DATE NOT NULL,
    AUTOR VARCHAR(100),
    MENSAJE VARCHAR(100),
    CANAL VARCHAR(100)
);


CREATE TABLE RESULTADO_PARTIDO (
    FECHA DATE NOT NULL,
    EQUIPO VARCHAR(100),
    NUM_CAMISETA INTEGER NOT NULL,
    JUGADOR VARCHAR(100) NOT NULL,
    ACCION VARCHAR(100),
    MINUTO INTEGER,
    MINUTO_COMPLEMENTARIO VARCHAR(100),
    TITULAR BOOLEAN NOT NULL,
    LINK_DATOS_JUGADOR VARCHAR(100) NOT NULL,
    LINK_DATOS_PARTIDO VARCHAR(100) NOT NULL
);
