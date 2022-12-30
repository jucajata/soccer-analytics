# soccer-analytics
Pasos para la instalación:

1. Realizar la copia del repositorio en el entorno local:
```
git clone https://github.com/jucajata/soccer-analytics.git
```

2. Instalar postgreSQL teniendo en cuenta el Sistema Operativo:
```
https://www.postgresql.org/download/
```

3. En la carpeta del proyecto crear un entorno virtual y activarlo:
```
python3 -m venv venv
```

4. Instalar las dependencias:
```
pip install -r requirements.txt
```

5. Ingresar a PostgreSQL y asignar una contraseña al usuario postgres:
```
sudo -su postgres

psql

ALTER ROLE postgres WITH PASSWORD 'contraseña';
```

6. Salir de PostgreSQL y modificar el archivo pg_hba.conf (sudo nano pg_hba.conf) ubicado en:
```
/etc/postgresql/15/main (modificar el 15 de acuerdo con la versión de postgreSQL)

Al usuario 'postgres' cambiar el método de autenticación de 'trust' a 'md5', el cual solicitará la contraseña.

Guardar los cambios.
```

7. Reiniciar el servicio de PostgreSQL luego de realizar los cambios en el numeral 6:
```
sudo /etc/init.d/postgresql restart
```


8. Ingresar a postgreSQL y crear una nueva base de datos:
```
sudo -su postgres

psql

(ingresar contraseña del usuario postgres asignada en el numeral 5)

CREATE DATABASE database_name
```

9. Conectarse a la nueva base de datos y crear las tablas que están en el archivo create_tables.sql:
```
\c database_name

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
```

10. En la carpeta del proyecto crear un archivo oculto para almacenar las variables de entorno:
```
nano .env

POSTGRES_DBNAME='database_name'
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='password'
```


