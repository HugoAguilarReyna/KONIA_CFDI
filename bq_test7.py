import etl_fiscal

matriz, detalle, traz, t = etl_fiscal.generar_reportes_mes('2026-02', limite_cfdi=20000)
conceptos_fijos = [
    '2. (-) Notas de Crédito (01)',
    '7. (-) Anticipo (07)',
]
segmentos_fijos = ['PPD', 'PUE']

print('\n==== Inspecting matriz array strictly ====')
found_something = False
for item in matriz:
    if item['concepto'] in conceptos_fijos:
        print(f"{item['segmento']} - {item['concepto']}: {item['monto']}")
        found_something = True

if not found_something:
    print('Ningún egreso llegó a la variable matriz!')
