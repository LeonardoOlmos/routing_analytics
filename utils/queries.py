# Query utilizada para obtener la información de los shipments que serán excluidos
# debido a que la condición para cruzar por SHP_DATE_DISPATCHED_ID no se cumple en la tabla de "routes"
INVALID_ROUTES_QUERY = """
SELECT 
    s.SHP_DATE_DISPATCHED_ID, 
    s.SHP_LG_FACILITY_ID, 
    s.SHP_LG_ROUTE_ID, 
    r.SHP_DATE_DISPATCHED_ID AS SHP_DATE_DISPATCHED_ID_R, 
    r.SHP_LG_FACILITY_ID AS SHP_LG_FACILITY_ID_R, 
    r.SHP_LG_ROUTE_ID AS SHP_LG_ROUTE_ID_R
FROM shipments s
LEFT JOIN routes r 
    ON r.SHP_LG_FACILITY_ID = s.SHP_LG_FACILITY_ID
    AND r.SHP_LG_ROUTE_ID = s.SHP_LG_ROUTE_ID
    AND r.SHP_DATE_DISPATCHED_ID = s.SHP_DATE_DISPATCHED_ID
WHERE r.SHP_LG_ROUTE_ID IS NULL;
"""

# Query utilizada para cruzar mis tablas routes y shipments, mediante las columnas SHP_LG_FACILITY_ID, SHP_LG_ROUTE_ID y SHP_DATE_DISPATCHED_ID
# En este caso hice uso de un INNER JOIN, ya que me importan aquellos envíos asignados a rutas existentes en mi tabla de "routes"
# julianday() se utilizo debido a que el manejador de bases de datos no soporta un casteo mediante CAST() o ::DATA_TYPE
SHIPMENTS_BY_ROUTE_QUERY = """
SELECT 
    s.SHP_SHIPMENT_ID,
    s.SHP_DATE_DISPATCHED_ID AS fecha,
    s.SHP_LG_FACILITY_ID AS service_center,
    r.CYCLE_FLAG AS ciclo,
    s.SHP_LG_ROUTE_ID AS route_id,
    r.SHP_LG_PLANNED_VEHICLE_TYPE AS "vehículo_plan",
    r.SHP_LG_VEHICLE_TYPE AS "vehículo_real",
    r.SHP_COMPANY_NAME AS carrier,
    r.DRIVER_CAREER AS experiencia_del_driver,
    r.DELIVERY_MODEL AS delivery_model,
    r.IS_PLANNED,
    s.SHP_LAST_SUB_STATUS,
    ROUND(
        (julianday(COALESCE(r.SHP_LG_END_DATE, r.LAST_STOP)) - julianday(r.SHP_LG_INIT_DATE)) * 24,
        4
    ) AS horas_ruta 
FROM shipments s
JOIN routes r 
    ON r.SHP_LG_FACILITY_ID = s.SHP_LG_FACILITY_ID
    AND r.SHP_LG_ROUTE_ID = s.SHP_LG_ROUTE_ID
    AND r.SHP_DATE_DISPATCHED_ID = s.SHP_DATE_DISPATCHED_ID
WHERE r.LAST_STOP IS NOT NULL;
"""

# Query utilizada para obtener la información agrupada por los campos solicitados para el ejercicio 1
# SUM(CASE WHEN IS_PLANNED = 1 THEN 1 ELSE 0 END) puede ser sustituida por SUM(IS_PLANNED) ya que solo tiene 1 y 0 pero se decidió manejar así en caso de que exisitieran otros valores
# Revisar IN en vez de LIKE
PRODUCTIVITY_QUERY = """
SELECT 
    fecha,
    service_center,
    ciclo,
    route_id,
    "vehículo_plan",
    "vehículo_real",
    carrier,
    experiencia_del_driver,
    delivery_model,
    SUM(CASE WHEN IS_PLANNED = 1 THEN 1 ELSE 0 END) AS shipments_planeados,
    COUNT(DISTINCT SHP_SHIPMENT_ID) AS shipments_despachados,
    SUM(CASE WHEN SHP_LAST_SUB_STATUS LIKE '%delivered%' THEN 1 ELSE 0 END) AS shipments_entregados,
    MAX(horas_ruta) AS ORH,
    SUM(CASE WHEN SHP_LAST_SUB_STATUS LIKE '%delivered%' THEN 1 ELSE 0 END) / MAX(horas_ruta) AS SPORH
FROM shipments_por_ruta
GROUP BY 1, 2, 3, 4, 5, 6 ,7 ,8 ,9;
"""