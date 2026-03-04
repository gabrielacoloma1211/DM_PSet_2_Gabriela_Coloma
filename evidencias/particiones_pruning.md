Partitions:
<img width="1019" height="359" alt="Screenshot 2026-03-04 at 2 25 46 AM" src="https://github.com/user-attachments/assets/43a3eb55-7ed2-45d7-952f-6bd99da175ed" />
<img width="1021" height="309" alt="Screenshot 2026-03-04 at 2 25 54 AM" src="https://github.com/user-attachments/assets/4e838411-cb20-40c2-9d5b-58873201765b" />
<img width="1021" height="411" alt="Screenshot 2026-03-04 at 2 26 03 AM" src="https://github.com/user-attachments/assets/dfe426f3-599e-48e9-811b-6ceee149ffff" />
<img width="956" height="583" alt="Screenshot 2026-03-04 at 2 26 14 AM" src="https://github.com/user-attachments/assets/5c7e1828-bd8a-408d-a171-72ed00528699" />
<img width="895" height="585" alt="Screenshot 2026-03-04 at 2 26 23 AM" src="https://github.com/user-attachments/assets/da0ec887-b4bb-4ea6-8de0-dbce70c3b859" />


Pruning: 


<img width="942" height="660" alt="Screenshot 2026-03-04 at 2 29 54 AM" src="https://github.com/user-attachments/assets/0e32c24f-23c8-4417-b451-718104e943bc" />

Para la consulta sobre el año 2024 del mes de febrero podemos ver que solo usa la partición de ese mes. Podemos verlo en la siguiente línea: Seq Scan on analytics_gold.fct_trips_2024_02. 


<img width="1008" height="643" alt="Screenshot 2026-03-04 at 2 30 06 AM" src="https://github.com/user-attachments/assets/13810ddf-f3b8-4a3e-903a-392a858f9a0c" />
Igual para la consulta sobre la tabla dim_zone podemos ver que solo busca en : Index Scan using dim_zone_p0_pkey on analytics_gold.dim_zone_p0 que es solo la partición que necesita en este caso. 
