import etl_fiscal
import traceback

try:
    data = etl_fiscal.extraer_datos_mes('2026-02', limite=20000)
    df = data.get('cfdis_base')
    rels = data.get('relaciones_origen')
    print('df cols:', df.columns.tolist())
    print('rels cols:', rels.columns.tolist())
    
    matriz, detalle, traz, t = etl_fiscal.generar_reportes_mes('2026-02', limite_cfdi=20000)
    print("SUCCESS")
except Exception as e:
    with open('error_log.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    print("ERROR WRITTEN TO error_log.txt")
