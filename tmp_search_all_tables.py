from google.cloud import bigquery

client = bigquery.Client(project='csreporter-iso27001')
uuid = '74F11F72-2EB5-468F-9FD1-48FBBE80C56E'.upper()
dataset_id = 'csmonitor'

tables = client.list_tables(dataset_id)
for table in tables:
    table_name = table.table_id
    try:
        # Check if table has a column that might contain UUID
        table_obj = client.get_table(f"{client.project}.{dataset_id}.{table_name}")
        columns = [c.name for c in table_obj.schema]
        
        uuid_cols = [c for c in columns if 'uuid' in c.lower() or 'id_documento' in c.lower() or 'id_document_relacionado' in c.lower()]
        if not uuid_cols:
            continue
            
        for col in uuid_cols:
            q = f"SELECT {col}, COUNT(*) FROM `{client.project}.{dataset_id}.{table_name}` WHERE UPPER({col}) = '{uuid}' GROUP BY 1"
            df = client.query(q).to_dataframe()
            if not df.empty:
                print(f"!!! FOUND UUID in table {table_name}, column {col} !!!")
                # Show some context
                qc = f"SELECT * FROM `{client.project}.{dataset_id}.{table_name}` WHERE UPPER({col}) = '{uuid}' LIMIT 1"
                dfc = client.query(qc).to_dataframe()
                print(dfc.T)
    except Exception as e:
        pass
print("Search finished.")
