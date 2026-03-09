import etl_fiscal
import pandas as pd
res = etl_fiscal.extraer_datos_mes('2026-02', limite=20000)
df = res['cfdis_base']
rels = res['relaciones_origen']

if not rels.empty:
    df = df.merge(rels, left_on='id', right_on='child_id', how='left')

df['Segmento'] = df.apply(etl_fiscal.definir_segmento, axis=1)

res_concepto = df.apply(etl_fiscal.clasificar_concepto, axis=1, result_type='expand')
df['Concepto_Financiero'] = res_concepto[0]
df['Monto_Real'] = res_concepto[1]

# NOTE: THIS IS WHAT THE ORIGINAL ETL DOES:
# groupby Segmento, Concepto_Financiero, sum Monto_Real, reset_index
df_agg = df.groupby(['Segmento', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()

concepto = '7. (-) Anticipo (07)'
seg = 'PUE'
filtro = df_agg[(df_agg['Segmento'] == seg) & (df_agg['Concepto_Financiero'] == concepto)]
monto = filtro['Monto_Real'].sum()
print(f"TEST CON GROUPBY: {seg} - {concepto}: {monto}")

# TEST NO GROUPBY:
filtro_raw = df[(df['Segmento'] == seg) & (df['Concepto_Financiero'] == concepto)]
monto_raw = filtro_raw['Monto_Real'].sum()
print(f"TEST SIN GROUPBY: {seg} - {concepto}: {monto_raw}")
