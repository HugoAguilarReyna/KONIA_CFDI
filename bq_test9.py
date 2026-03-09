import etl_fiscal
import pandas as pd
res = etl_fiscal.extraer_datos_mes('2026-02', limite=20000)
df = res['cfdis_base']
rels = res['relaciones_origen']
pagos = res['pagos_reps']

if not rels.empty:
    df = df.merge(rels, left_on='id', right_on='child_id', how='left')

df['Segmento'] = df.apply(etl_fiscal.definir_segmento, axis=1)
res_concepto = df.apply(etl_fiscal.clasificar_concepto, axis=1, result_type='expand')
df['Concepto_Financiero'] = res_concepto[0]
df['Monto_Real'] = res_concepto[1]

if not pagos.empty:
    pagos['fecha_pago'] = pd.to_datetime(pagos['fecha_pago'])
    pagos['imp_pagado'] = pd.to_numeric(pagos['imp_pagado'], errors='coerce').fillna(0.0)

    pagos_detalle = pagos.copy()
    pagos_detalle['tipo'] = 'P'
    pagos_detalle['metodo_pago'] = 'PPD'
    pagos_detalle['Segmento'] = 'PPD'
    pagos_detalle['Flujo'] = 'EMITIDOS'
    pagos_detalle['Concepto_Financiero'] = '8. (-) Pagos Aplicados (08/09)'
    pagos_detalle['Monto_Real'] = pagos_detalle['imp_pagado'] * -1
    pagos_detalle.rename(columns={'uuid_factura': 'uuid'}, inplace=True)
    for col_name in ['id', 'total']:
        pagos_detalle[col_name] = None

    df = pd.concat([df, pagos_detalle], ignore_index=True, sort=False)

df_agg = df.groupby(['Segmento', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()

print('\n==== df_agg types inside loop ====')
print(df_agg.dtypes)

print('\n==== Extracting exact values in df_agg ====')
for i, row in df_agg.iterrows():
    print(f"{repr(row['Segmento'])} | {repr(row['Concepto_Financiero'])} | {row['Monto_Real']}")

conceptos_fijos = [
    '2. (-) Notas de Crédito (01)',
    '7. (-) Anticipo (07)',
]
segmentos_fijos = ['PPD', 'PUE']

print('\n==== Filter test inside Loop ====')
for seg in segmentos_fijos:
    for concepto in conceptos_fijos:
        filtro = df_agg[(df_agg['Segmento'] == seg) & (df_agg['Concepto_Financiero'] == concepto)]
        monto = filtro['Monto_Real'].sum()
        print(f"{seg} - {concepto}: {monto} (filtro filas: {len(filtro)})")
