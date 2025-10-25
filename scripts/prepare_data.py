import os
import shutil

BASE = os.path.dirname(os.path.dirname(__file__))
ARCHIVOS = os.path.join(BASE, 'Archivos')
DATA = os.path.join(BASE, 'data')

mappings = {
    'Anexo1.NoFetal2019_CE_15-03-23.xlsx': 'NoFetal2019.xlsx',
    'Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx': 'CodigosDeMuerte.xlsx',
    'Divipola_CE_.xlsx': 'Divipola.xlsx',
}

os.makedirs(DATA, exist_ok=True)

for src_name, dest_name in mappings.items():
    src = os.path.join(ARCHIVOS, src_name)
    dest = os.path.join(DATA, dest_name)
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f'Copied: {src_name} -> data/{dest_name}')
    else:
        print(f'Not found in Archivos/: {src_name} (skipping)')

print('Done.')
