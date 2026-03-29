import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging
import os

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Config (set via environment variables or edit directly) ───────────────────
CSV_FILE   = os.getenv("CSV_FILE",   "data.csv")
DB_HOST    = os.getenv("DB_HOST",    "localhost")
DB_PORT    = int(os.getenv("DB_PORT", 3306))
DB_NAME    = os.getenv("DB_NAME",    "etl_db")
DB_USER    = os.getenv("DB_USER",    "root")
DB_PASS    = os.getenv("DB_PASS",    "password")
TABLE_NAME = os.getenv("TABLE_NAME", "etl_output")


# ── EXTRACT ───────────────────────────────────────────────────────────────────
def extract(filepath: str) -> pd.DataFrame:
    log.info(f"Extracting data from: {filepath}")
    df = pd.read_csv(filepath)
    log.info(f"Extracted {len(df)} rows, {len(df.columns)} columns")
    log.info(f"Columns: {list(df.columns)}")
    return df


# ── TRANSFORM ─────────────────────────────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Starting transformation...")

    original_rows = len(df)

    # 1. Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # 2. Strip whitespace from string values
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # 3. Log null counts before cleaning
    null_counts = df.isnull().sum()
    log.info(f"Null values before cleaning:\n{null_counts[null_counts > 0]}")

    # 4. Fill numeric nulls with column mean
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        if df[col].isnull().any():
            mean_val = round(df[col].mean(), 2)
            df[col].fillna(mean_val, inplace=True)
            log.info(f"Filled nulls in '{col}' with mean: {mean_val}")

    # 5. Fill string/object nulls with 'Unknown'
    string_cols = df.select_dtypes(include="object").columns
    for col in string_cols:
        if df[col].isnull().any():
            df[col].fillna("Unknown", inplace=True)
            log.info(f"Filled nulls in '{col}' with 'Unknown'")

    # 6. Drop rows that are entirely empty
    df.dropna(how="all", inplace=True)

    log.info(f"Transformation complete: {original_rows} → {len(df)} rows")
    return df


# ── LOAD ──────────────────────────────────────────────────────────────────────
def load(df: pd.DataFrame):
    log.info(f"Connecting to MySQL at {DB_HOST}:{DB_PORT}...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()

        # Build CREATE TABLE dynamically from DataFrame columns
        col_definitions = []
        for col, dtype in df.dtypes.items():
            if "int" in str(dtype):
                sql_type = "INT"
            elif "float" in str(dtype):
                sql_type = "FLOAT"
            else:
                sql_type = "VARCHAR(255)"
            col_definitions.append(f"`{col}` {sql_type}")

        create_sql = f"""
            CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {', '.join(col_definitions)}
            )
        """
        cursor.execute(create_sql)
        log.info(f"Table '{TABLE_NAME}' ready")

        # Insert rows
        cols = ", ".join([f"`{c}`" for c in df.columns])
        placeholders = ", ".join(["%s"] * len(df.columns))
        insert_sql = f"INSERT INTO `{TABLE_NAME}` ({cols}) VALUES ({placeholders})"

        rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
        cursor.executemany(insert_sql, rows)
        conn.commit()

        log.info(f"✅ Loaded {cursor.rowcount} rows into '{TABLE_NAME}'")

    except Error as e:
        log.error(f"❌ MySQL error: {e}")
        raise
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            log.info("MySQL connection closed")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def run_etl():
    log.info("=" * 50)
    log.info("ETL Pipeline Started")
    log.info("=" * 50)
    df = extract(CSV_FILE)
    df = transform(df)
    load(df)
    log.info("=" * 50)
    log.info("ETL Pipeline Completed Successfully")
    log.info("=" * 50)


if __name__ == "__main__":
    run_etl()
