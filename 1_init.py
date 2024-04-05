import os 
import sys
import glob
import time
import logging
import psycopg2
import fileinput

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('1_init')

logger.info('[*] Starting 1_init.py')

try:
    conn = psycopg2.connect("dbname='digantara' user='postgres' host='postgis' password='postgis'")
    conn.autocommit = True
    curs = conn.cursor()
    logger.info('[*] Connection Successful')
except:
    logger.error("[!] Connection Failed")

try:

    ## SCHEMA FOR USER TABLE
    curs.execute("""
    CREATE TABLE IF NOT EXISTS public.user (
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50),
        email VARCHAR(50) NOT NULL,
        location_longitude DOUBLE PRECISION,
        location_latitude DOUBLE PRECISION
    )
    """)
    logger.info('[*] Created user Table')

    ## SCHEMA FOR CONFIGURATION TABLE
    curs.execute("""
    CREATE TABLE IF NOT EXISTS public.configuration (
        config_id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES public.user(user_id),
        config_name VARCHAR(50) NOT NULL
    )
    """)
    logger.info('[*] Created configuration Table')

    ## SCHEMA FOR OBJECT TABLE
    curs.execute("""
    CREATE TABLE IF NOT EXISTS public.object (
        object_id SERIAL PRIMARY KEY,
        creat_ts TIMESTAMP WITH TIME ZONE
    )
    """)
    logger.info('[*] Created object Table')

    ## SCHEMA FOR OBJECT HIST TABLE
    curs.execute("""
    CREATE TABLE IF NOT EXISTS public.object_hist (
        object_id INTEGER REFERENCES public.object(object_id),
        creat_ts TIMESTAMP WITH TIME ZONE,
        eccentricity DOUBLE PRECISION,
        semimajor_axis DOUBLE PRECISION,
        inclination DOUBLE PRECISION,
        raan DOUBLE PRECISION,
        argument_of_periapsis DOUBLE PRECISION,
        true_anomaly DOUBLE PRECISION,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        altitude DOUBLE PRECISION,
        x DOUBLE PRECISION,
        y DOUBLE PRECISION,
        z DOUBLE PRECISION,
        velocity_x DOUBLE PRECISION,
        velocity_y DOUBLE PRECISION,
        velocity_z DOUBLE PRECISION
    )
    """)
    logger.info('[*] Created object_hist Table')

    ## SCHEMA FOR OBJECT & CONFIG MAPPING
    curs.execute("""
    CREATE TABLE IF NOT EXISTS public.object_config_map (
        map_id SERIAL PRIMARY KEY,
        object_id INTEGER REFERENCES public.object(object_id),
        config_id INTEGER REFERENCES public.configuration(config_id)
    )
    """)
    logger.info('[*] Created object_config_map Table')

    ## CHECK IF OBJECT INGESTION HAS ALREADY BEEN PERFORMED OR NOT
    curs.execute("""
    SELECT COUNT(*)
    FROM public.object_hist
    """)
    count = curs.fetchone()[0]

    # Ingest if object_hist Table is Empty
    if count == 0:

        ## TRUNCATE & LOAD OBJECT DATA
        curs.execute("""
        TRUNCATE TABLE public.object_hist, public.object, public.object_config_map
        """)
        logger.info('[*] Truncated tables for data load')

        # Add object id to each csv
        dir_path = os.path.dirname(os.path.realpath(__file__))
        csv_files = glob.glob('Assignment data/*.csv')
        logger.info(f'[*] Found {len(csv_files)} CSV files')

        start_time = time.time()
        for f in csv_files:
            obj_id = f.split('/')[1].split('.')[0]

            curs.execute(f"""
            INSERT INTO public.object (object_id, creat_ts) VALUES ({obj_id}, CURRENT_TIMESTAMP)
            """)

            for line in fileinput.input([f'{dir_path}/{f}'], inplace=True):
                # Don't add object id if already present
                if len(line.split(',')) == 17:
                    sys.stdout.write(f'{line}')
                else:
                    sys.stdout.write(f'{obj_id},{line}')

            with open(f'{dir_path}/{f}', 'r') as f2:
                next(f2) # Skip header
                curs.copy_from(f2, 'object_hist', sep=',')
        end_time = time.time()
        diff = end_time - start_time
        logger.info(f'[*] Successfuly ingested {len(csv_files)} CSV files in {round(diff,2)} seconds')
    else:
        logger.info('[*] Skipping ingestion')

except (Exception, psycopg2.DatabaseError) as error:
    logger.error(error)

conn.close()
