from pathlib import Path
import json
import re

path = Path(__file__).parent

def PascalCase(str): # why genshin optimizer why
    return re.sub(" ", "", re.sub("[^A-Za-z0-9 ]+", "", re.sub("-", " ", str)).title())

f_mat_excel = open(path / "MaterialExcelConfigData.json")
mat_data = json.load(f_mat_excel)
f_mat_excel.close()

f_textmap = open(path / "TextMapEN.json", "r", encoding="utf-8")
textmap_data = json.load(f_textmap)
f_textmap.close()

f_lua = open(path / "material_names.lua", "w", encoding="utf-8")
f_lua.write("local material_names = {\n")

skips = 0

for i in mat_data:
    hash = str(i["nameTextMapHash"])
    if hash not in textmap_data or not PascalCase(textmap_data[hash]):
        print(f'skipped {i["id"]}')
        skips += 1
        continue
    f_lua.write(f'\t[{i["id"]}] = "{PascalCase(textmap_data[hash])}",\n')

f_lua.write("}\nreturn material_names")
f_lua.close()

print(f'skipped total: {skips}')