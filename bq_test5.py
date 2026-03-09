import etl_fiscal

matriz, detalle, traz, t = etl_fiscal.generar_reportes_mes('2026-02', limite_cfdi=20000)

print('\n==== Final Matriz Elements from generar_reportes_mes ====')
for item in matriz:
    if item['monto'] != 0.0:
        print(f"{item['segmento']} - {item['concepto']}: {item['monto']}")
