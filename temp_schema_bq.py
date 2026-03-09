import base64
import sys
from google.cloud import bigquery

# The credentials should be picked up from the environment or default application credentials
try:
    bq_client = bigquery.Client(project="csreporter-iso27001")
    # Let's get one row from public_cfdi_pagos
    query = "SELECT * FROM `csreporter-iso27001.csmonitor.public_cfdi_pagos` LIMIT 1"
    res = bq_client.query(query).to_dataframe()
    print("public_cfdi_pagos schema:")
    print(res.dtypes)
    
except Exception as e:
    print("Error:", e)
