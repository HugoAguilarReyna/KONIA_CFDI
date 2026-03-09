from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project='csreporter-iso27001')
uuid = '74F11F72-2EB5-468F-9FD1-48FBBE80C56E'.upper()
dataset = 'csmonitor'

tables = ['public_cfdis', 'public_cfdi_comprobantes', 'public_cfdi_pagos']
found = False

for table_id in tables:
    try:
        q = f'SELECT * FROM `{dataset}.{table_id}` WHERE UPPER(uuid) = "{uuid}"'
        df = client.query(q).to_dataframe()
        if not df.empty:
            print(f"FOUND IN {table_id}")
            print(df.T)
            found = True
    except Exception as e:
        print(f"Error checking {table_id}: {e}")

if not found:
    print("Not found in common tables. Scanning for UUID in related columns...")
    q2 = f"SELECT * FROM `{dataset}.public_cfdi_pago_documentos_relacionados` WHERE UPPER(id_documento) = '{uuid}'"
    df2 = client.query(q2).to_dataframe()
    if not df2.empty:
        print("FOUND in public_cfdi_pago_documentos_relacionados:")
        print(df2.T)
