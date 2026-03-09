import etl_fiscal
import pandas as pd

matriz, detalle, traz, t = etl_fiscal.generar_reportes_mes('2026-02', limite_cfdi=20000)
conceptos_fijos = [
    '2. (-) Notas de Crédito (01)',
    '7. (-) Anticipo (07)',
]

print('\n==== Final Aggregation ====')
for item in matriz:
    if item['concepto'] in conceptos_fijos:
        print(f"{item['segmento']} - {item['concepto']}: {item['monto']}")
