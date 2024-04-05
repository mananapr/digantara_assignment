import logging
import psycopg2
import datetime as dt

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('3_benchmark')

logger.info('[*] Starting 3_benchmark.py')

try:
    conn = psycopg2.connect("dbname='digantara' user='postgres' host='postgis' password='postgis'")
    conn.autocommit = True
    logger.info('[*] Connection Successful')
except:
    logger.error("[!] Connection Failed")


with conn.cursor() as curs:

    try:
        ## CREATE MAIN PARTITIONED TABLE
        curs.execute("""
        DROP TABLE IF EXISTS object_hist_partitioned;
        CREATE TABLE object_hist_partitioned (LIKE object_hist INCLUDING ALL) PARTITION BY RANGE(creat_ts);
        """)
        logger.info('[*] Empty partition table created')

        ## CREATE MONTH LEVEL PARTITION TABLES
        start_point = dt.datetime(2022,2,1)
        end_point = dt.datetime(2023,6,1)
        flag = True
        while flag:
            # Define month end point
            partition_end_point = start_point + dt.timedelta(days=31)
            partition_end_point = partition_end_point.replace(day = 1)
            curs.execute(f"""
            CREATE TABLE object_hist_{start_point.strftime('%Y%m')} PARTITION OF object_hist_partitioned
            FOR VALUES FROM ('{start_point.strftime("%Y-%m-%d")}') TO ('{partition_end_point.strftime("%Y-%m-%d")}');
            """)
            # Increment start point to next month
            start_point = partition_end_point
            if start_point > end_point:
                flag = False
        # Create default partition table in case of additional data
        curs.execute(f"""
        CREATE TABLE object_hist_default PARTITION OF object_hist_partitioned DEFAULT;
        """)
        logger.info('[*] Successfully created date partitions')

        ## INGEST DATA INTO PARTITIONED TABLE
        curs.execute(f"""
        INSERT INTO object_hist_partitioned SELECT * FROM object_hist;
        """)
        logger.info('[*] Data successfully loaded into partition table -> object_hist_paritioned')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
