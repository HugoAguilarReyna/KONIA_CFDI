import etl_fiscal

client = etl_fiscal.bq_client
dataset = f"{etl_fiscal.CONFIG['project_id']}.{etl_fiscal.CONFIG['dataset_id']}"

queries = {
    'Facturas con Pago': f"SELECT count(*) as c FROM `{dataset}.public_cfdi_pago_documentos_relacionados` doc JOIN `{dataset}.public_cfdis` parent ON UPPER(parent.uuid) = UPPER(doc.id_documento) WHERE FORMAT_DATE('%Y-%m', parent.fecha_emision) = '2026-02' AND parent.estatus = 'vigente'",
    'Egresos': f"SELECT count(*) as c FROM `{dataset}.public_cfdis` WHERE FORMAT_DATE('%Y-%m', fecha_emision) = '2026-02' AND estatus = 'vigente' AND tipo = 'E'",
    'Anticipos': f"SELECT count(*) as c FROM `{dataset}.public_cfdi_relacionados` r JOIN `{dataset}.public_cfdis` parent ON r.uuid_relacionado = parent.uuid WHERE FORMAT_DATE('%Y-%m', parent.fecha_emision) = '2026-02' AND parent.estatus = 'vigente' AND r.tipo_relacion = '07'",
    'Total': f"SELECT count(*) as c FROM `{dataset}.public_cfdis` WHERE FORMAT_DATE('%Y-%m', fecha_emision) = '2026-02' AND estatus = 'vigente'"
}

for k, q in queries.items():
    res = client.query(q).result()
    for row in res:
        print(f"{k}: {row.c}")
