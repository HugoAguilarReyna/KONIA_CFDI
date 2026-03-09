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

COLS_RFC = ['rfc_emisor', 'nombre_emisor', 'rfc_receptor', 'nombre_receptor']
for col_name in COLS_RFC:
    df[col_name] = df.groupby('uuid')[col_name].transform(
        lambda s: s.ffill().bfill()
    )

uuids_aun_null = df[df['rfc_emisor'].isna()]['uuid'].dropna().unique().tolist()
if uuids_aun_null:
    df_lookup = etl_fiscal.fetch_emisor_receptor_por_uuids(uuids_aun_null)
    if not df_lookup.empty:
        df_lookup['uuid_upper'] = df_lookup['uuid'].str.upper()
        lookup_map = df_lookup.set_index('uuid_upper')[COLS_RFC].to_dict(orient='index')

        def fill_from_lookup(row):
            key = str(row.get('uuid', '')).upper()
            if pd.isna(row.get('rfc_emisor')) and key in lookup_map:
                for c in COLS_RFC:
                    row[c] = lookup_map[key].get(c)
            return row

        # THIS IS THE SUSPECT AREA
        print('\n==== ANTES DEL APPLY ====')
        print(df[df['Concepto_Financiero'] == '7. (-) Anticipo (07)']['Monto_Real'].sum())
        
        df = df.apply(fill_from_lookup, axis=1)

        print('\n==== DESPUES DEL APPLY ====')
        print(df[df['Concepto_Financiero'] == '7. (-) Anticipo (07)']['Monto_Real'].sum())
