import pandas as pd
from sqlalchemy import create_engine, text
import traceback
import warnings
from config.config import CONNECTION_STRING
warnings.simplefilter("ignore")

from logger import general_logger, dir_logger
from datetime import datetime

# Define connection string for SQLAlchemy
conn_str = CONNECTION_STRING

# Create SQLAlchemy engine
engine = create_engine(conn_str)

def getDataFromDfandInsertInDB(df):
    try:
        df['request_date'].fillna(pd.Timestamp('1900-01-01'), inplace=True)
        df['patient_last_name'].fillna("", inplace=True)
        df = df.drop(columns=['id'])
        df.drop_duplicates(inplace=True)
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

        # Insert row-by-row
        with engine.begin() as conn:
            for index, row in df.iterrows():
                try:
                    row_dict = row.to_dict()
                    insert_query = text("""
                        INSERT INTO patient_data 
                        (patient_first_name, patient_last_name, dob, request_date, 
                        old_document, new_document, old_document_path, new_document_path, is_deleted) 
                        VALUES (:patient_first_name, :patient_last_name, :dob, :request_date, 
                        :old_document, :new_document, :old_document_path, :new_document_path, :is_deleted)
                    """)
                    conn.execute(insert_query, row_dict)
                except Exception as row_error:
                    general_logger.error(f"Error inserting row {index}: {row_error}", exc_info=True)
                    print(f"Error inserting row {index}, skipping...")

        print("Data updated successfully.")
        return True

    except Exception as e:
        print("Error occurred in main function:")
        traceback.print_exc()
        general_logger.error(f"Main function error: {e}", exc_info=True)
        return False