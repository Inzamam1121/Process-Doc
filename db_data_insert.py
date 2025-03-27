import pandas as pd
from sqlalchemy import create_engine, text
import traceback
import warnings
from config.config import CONNECTION_STRING
warnings.simplefilter("ignore")

import logging
from datetime import datetime

# Configure logging
log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    filename="Logs/"+log_filename,
    level=logging.ERROR,  # Log only errors and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Define connection string for SQLAlchemy
conn_str = CONNECTION_STRING

# Create SQLAlchemy engine
engine = create_engine(conn_str)

def getDataFromDfandInsertInDB(df):
    try:
        df['request_date'].fillna(pd.Timestamp('1900-01-01'), inplace=True)
        df['patient_last_name'].fillna("", inplace=True)
        df = df.drop(columns=['id'])
        df.drop_duplicates()
        df["dob"] = pd.to_datetime(df["dob"], errors='coerce')
        df["request_date"] = pd.to_datetime(df["request_date"], errors='coerce')

        old_documents = df["old_document"].dropna().unique().tolist()

        if old_documents:
            with engine.connect() as conn:
                placeholders = ", ".join([f":doc{i}" for i in range(len(old_documents))])
                delete_query = text(f"DELETE FROM patient_data WHERE old_document IN ({placeholders})")
                params = {f"doc{i}": doc for i, doc in enumerate(old_documents)}
                conn.execute(delete_query, params)
                conn.commit()

        df.to_sql("patient_data", con=engine, if_exists="append", index=False, method="multi")
        print("Data updated successfully.")
        return True
    except Exception as e:
        print("Error occurred:")
        traceback.print_exc()
        logging.error(f"An error occurred {e}", exc_info=True)
        return False