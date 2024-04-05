import logging
import psycopg2

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('1_init')

logger.info('[*] Starting 2_sql_query.py')

try:
    conn = psycopg2.connect("dbname='digantara' user='postgres' host='postgis' password='postgis'")
    conn.autocommit = True
    logger.info('[*] Connection Successful')
except:
    logger.error("[!] Connection Failed")



# we use a context manager to scope the cursor session
with conn.cursor() as curs:

    try:
        ## SELECT A RANDOM TIME
        curs.execute("""
        SELECT creat_ts
        FROM public.object_hist
        ORDER BY random()
        LIMIT 1
        """)
        time = curs.fetchone()[0]
        logger.info(f'[*] Random Time Select: {time}')

        ## SELECT 5 RANDOM OBJECTS AT THAT TIME (INPUT TABLE FOR TASK 2 A)
        curs.execute(f"""
        DROP TABLE IF EXISTS public.task_2_a_input;
        CREATE TABLE public.task_2_a_input AS
        SELECT longitude, latitude, creat_ts, object_id, x, y, z
        FROM public.object_hist
        WHERE creat_ts='{time}'
        ORDER BY random()
        LIMIT 5;
        """)
        curs.execute(f"""
        SELECT * FROM public.task_2_a_input
        """)
        random_points = curs.fetchall()
        logger.info(f'[*] Random Points Selected: {random_points}')

        ## GET ALL THE OBJECTS WITHIN THE PENTGAON FORMED BY THE 5 OBJECTS SELECTED EARLIER (OUTPUT TABLE FOR TASK 2 A)
        polygon_str = ''
        for row in random_points:
            polygon_str += f'{row[0]} {row[1]},'
        polygon_str += f'{random_points[0][0]} {random_points[0][1]}'
        curs.execute(f"""
        DROP TABLE IF EXISTS public.task_2_a_output;
        CREATE TABLE public.task_2_a_output AS
        SELECT a.*
        FROM (
            SELECT a.*, ST_SetSRID(ST_MakePoint(a.longitude, a.latitude), 4326) AS geom
            FROM public.object_hist AS a
            INNER JOIN public.task_2_a_input AS b
            ON a.creat_ts = b.creat_ts AND a.object_id <> b.object_id
        ) AS a
        WHERE ST_Contains(ST_GeomFromText('POLYGON(({polygon_str}))',4326), a.geom);
        """)
        logger.info('[*] Data for objects in the pentagon has been stored in -> task_2_a_output')

        ## SELECT 1 RANDOM OBJECT AT A GIVEN TIME (INPUT TABLE FOR TASK 2 B)
        curs.execute(f"""
        DROP TABLE IF EXISTS public.task_2_b_input;
        CREATE TABLE public.task_2_b_input AS
        SELECT longitude, latitude, creat_ts, object_id, x, y, z
        FROM public.task_2_a_input
        ORDER BY random()
        LIMIT 1;
        """)
        logger.info('[*] Data for random point (x, y, z) has been stored in -> task_2_b_input')

        ## FIND NEAREST POINT TO THE 1 RANDOM OBJECT SELECTED EARLIER (OUTPUT TABLE FOR TASK 2 B)
        curs.execute(f"""
        DROP TABLE IF EXISTS public.task_2_b_output;
        CREATE TABLE public.task_2_b_output AS
        SELECT a.object_id, a.x, a.y, a.z, b_x, b_y, b_z, a.geom <-> ST_MakePoint(b_x, b_y, b_z) AS dist
        FROM (
            SELECT a.*, ST_MakePoint(a.x, a.y, a.z) AS geom, b.x AS b_x, b.y AS b_y, b.z AS b_z
            FROM public.object_hist AS a
            INNER JOIN public.task_2_b_input AS b
            ON a.creat_ts = b.creat_ts and a.object_id <> b.object_id
        ) AS a
        ORDER BY
          dist
        LIMIT 1;
        """)
        logger.info('[*] Data for the nearest object has been stored in -> task_2_b_output')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
