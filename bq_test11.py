import etl_fiscal

def test_generar_reportes(periodo):
    start_total = etl_fiscal.time.time()
    
    res = etl_fiscal.extraer_datos_mes(periodo, limite=20000)
    if not res: return None
    
    df = res['cfdis_base']
    rels = res['relaciones_origen']
    pagos = res['pagos_reps']
    
    if not rels.empty:
        # Simplification: just assume rels is already pre-joined for this isolated test
        pass
    else:
        df['tipo_relacion'] = 'NA'
        df['metodo_padre'] = 'NA'
        
    df['Segmento'] = df.apply(etl_fiscal.definir_segmento, axis=1)
    df['Flujo'] = df.apply(lambda r: etl_fiscal.clasificar_flujo(r, etl_fiscal.CONFIG['rfc_empresa']), axis=1)
    res_concepto = df.apply(etl_fiscal.clasificar_concepto, axis=1, result_type='expand')
    df['Concepto_Financiero'] = res_concepto[0]
    df['Monto_Real'] = res_concepto[1]
    
    if not pagos.empty:
        pagos['fecha_pago'] = etl_fiscal.pd.to_datetime(pagos['fecha_pago'])
        pagos['Periodo'] = periodo
        pagos['imp_pagado'] = etl_fiscal.pd.to_numeric(pagos['imp_pagado'], errors='coerce').fillna(0.0)
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
        df = etl_fiscal.pd.concat([df, pagos_detalle], ignore_index=True, sort=False)
        
    COLS_RFC = ['rfc_emisor', 'nombre_emisor', 'rfc_receptor', 'nombre_receptor']
    for col_name in COLS_RFC:
        df[col_name] = df.groupby('uuid')[col_name].transform(lambda s: s.ffill().bfill())
        
    uuids_aun_null = df[df['rfc_emisor'].isna()]['uuid'].dropna().unique().tolist()
    if uuids_aun_null:
        df_lookup = etl_fiscal.fetch_emisor_receptor_por_uuids(uuids_aun_null)
        if not df_lookup.empty:
            df_lookup['uuid_upper'] = df_lookup['uuid'].str.upper()
            lookup_map = df_lookup.set_index('uuid_upper')[COLS_RFC].to_dict(orient='index')
            def fill_from_lookup(row):
                key = str(row.get('uuid', '')).upper()
                if etl_fiscal.pd.isna(row.get('rfc_emisor')) and key in lookup_map:
                    for c in COLS_RFC:
                        row[c] = lookup_map[key].get(c)
                return row
            df = df.apply(fill_from_lookup, axis=1)

    print('\n==== BEFORE GROUPBY ====')
    print('Sum ' + str(df[df['Concepto_Financiero'] == '7. (-) Anticipo (07)']['Monto_Real'].sum()))

    df_agg = df.groupby(['Segmento', 'Concepto_Financiero'])['Monto_Real'].sum().reset_index()

    print('\n==== AFTER GROUPBY ====')
    print(df_agg[df_agg['Concepto_Financiero'] == '7. (-) Anticipo (07)'])
    
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
            monto = df_agg[(df_agg['Segmento'] == seg) & (df_agg['Concepto_Financiero'] == concepto)]['Monto_Real'].sum()
            print(f"INSIDE LOOP -> {seg} - {concepto}: {monto}")
            matriz.append({'periodo': periodo, 'company_id': etl_fiscal.CONFIG['company_id'],
                           'segmento': seg, 'concepto': concepto, 'monto': monto})

test_generar_reportes('2026-02')
