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

df_agg = df.groupby(['Segmento', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()

conceptos_fijos = [
    '1. (+) Total Facturado',
    '2. (-) Notas de Crédito (01)',
    '3. (+) Nota de Débito (02)',
    '4. (-) Devoluciones (03)',
    '6. Traslado de mercancía (05,06)',
    '7. (-) Anticipo (07)',
    '8. (-) Pagos Aplicados (08/09)'
]
segmentos_fijos = ['PPD', 'PUE']

matriz = []
for seg in segmentos_fijos:
    for concepto in conceptos_fijos:
        # Check this exact logic used in etl_fiscal!
        monto = df_agg[(df_agg['Segmento'] == seg) & (df_agg['Concepto_Financiero'] == concepto)]['Monto_Real'].sum()
        matriz.append({'segmento': seg, 'concepto': concepto, 'monto': monto})

print('\nResultados Matriz:')
for item in matriz:
    if item['monto'] != 0.0:
        print(f"{item['segmento']} - {item['concepto']}: {item['monto']}")
