-- Query básica de la tabla resultado_partido
SELECT * 
FROM resultado_partido 
ORDER BY link_datos_partido, equipo, titular DESC;


-- Query para obtener los goles de cada partido organizado por minuto
SELECT subquery.fecha,
       subquery.equipo,
       subquery.jugador,
       subquery.accion,
       subquery.minuto,
       subquery.minuto_complementario,
       subquery.titular,
       S.equipo_local,
       S.resultado_local,
       S.resultado_visitante,
       S.equipo_visitante,
       S.competicion 
FROM (SELECT * 
      FROM resultado_partido
      WHERE accion IS NOT NULL
      AND (accion LIKE '%Gol%')
      ORDER BY link_datos_partido, minuto DESC) AS subquery 
INNER JOIN 
     (SELECT *
      FROM resultados_partidos) AS S
ON subquery.link_datos_partido = S.link_datos_partido;