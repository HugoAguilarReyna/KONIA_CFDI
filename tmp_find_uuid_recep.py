from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project='csreporter-iso27001')
uuid = '74F11F72-2EB5-468F-9FD1-48FBBE80C56E'.upper()
dataset = 'csmonitor'

q = f"SELECT * FROM `{dataset}.public_cfdi_recep_cfdis` WHERE UPPER(uuid) = '{uuid}'"
try:
    df = client.query(q).to_dataframe()
    if not df.empty:
        print("FOUND IN public_cfdi_recep_cfdis")
        print(df.T)
    else:
        print("Not found in public_cfdi_recep_cfdis")
except Exception as e:
    print(f"Error: {e}")
