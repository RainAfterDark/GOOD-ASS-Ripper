from pathlib import Path
import json
import re

path = Path(__file__).parent

def PascalCase(str): # why genshin optimizer why
    return re.sub(" ", "", re.sub("[^A-Za-z0-9 ]+", "", re.sub("-", " ", str)).title())

f_weap_excel = open(path / "WeaponExcelConfigData.json")
weap_data = json.load(f_weap_excel)
f_weap_excel.close()

f_textmap = open(path / "TextMapEN.json", "r", encoding="utf-8")
textmap_data = json.load(f_textmap)
f_textmap.close()

f_lua = open(path / "weapons.lua", "w", encoding="utf-8")
f_lua.write("local weapons = {\n")

skips = 0

for i in weap_data:
    hash = str(i["nameTextMapHash"])
    if hash not in textmap_data:
        print(f'skipped {i["id"]}')
        skips += 1
        continue
    key = PascalCase(textmap_data[hash])
    data = f'{{\n\t\tkey = "{key}",\n\t\trarity = {i["rankLevel"]}\n\t}}'
    f_lua.write(f'\t[{i["id"]}] = {data},\n')

f_lua.write("}\nreturn weapons")
f_lua.close()

print(f'skipped total: {skips}')