from pathlib import Path
import json
import re

path = Path(__file__).parent

def PascalCase(str): # why genshin optimizer why
    return re.sub(" ", "", re.sub("[^A-Za-z0-9 ]+", "", re.sub("-", " ", str)).title())

slot_names = {
    "EQUIP_BRACER": "flower",
    "EQUIP_NECKLACE": "plume",
    "EQUIP_SHOES": "sands",
    "EQUIP_RING": "goblet",
    "EQUIP_DRESS": "circlet"
}

f_textmap = open(path / "TextMapEN.json", "r", encoding="utf-8")
textmap_data = json.load(f_textmap)
f_textmap.close()

f_affix_excel = open(path / "EquipAffixExcelConfigData.json")
affix_data = json.load(f_affix_excel)
f_affix_excel.close()

skips = 0
affix_table = {}

for i in affix_data:
    hash = str(i["nameTextMapHash"])
    if hash not in textmap_data:
        print(f'skipped affix {i["id"]}')
        skips += 1
        continue
    affix_table[i["id"]] = textmap_data[hash]

f_set_excel = open(path / "ReliquarySetExcelConfigData.json")
set_data = json.load(f_set_excel)
f_set_excel.close()

set_table = {}

for i in set_data:
    if "equipAffixId" not in i:
        print(f'skipped set {i["setId"]}')
        skips += 1
        continue
    affix_id = i["equipAffixId"]
    set_table[i["setId"]] = affix_table[affix_id]

f_arti_excel = open(path / "ReliquaryExcelConfigData.json")
arti_data = json.load(f_arti_excel)
f_arti_excel.close()

f_lua = open(path / "artifacts.lua", "w", encoding="utf-8")
f_lua.write("local artifacts = {\n")

for i in arti_data:
    hash = str(i["nameTextMapHash"])
    if hash not in textmap_data:
        print(f'skipped artifact {i["id"]}')
        skips += 1
        continue
    name = PascalCase(textmap_data[hash])
    set = ""
    if "setId" in i and i["setId"] in set_table:
        set = PascalCase(set_table[i["setId"]])
    slot = slot_names[i["equipType"]]
    data = f'''{{
    \tname = "{name}",
    \tset = "{set}",
    \tslot = "{slot}",
    \trarity = {i["rankLevel"]}
    }}'''
    f_lua.write(f'\t[{i["id"]}] = {data},\n')

f_lua.write("}\nreturn artifacts")
f_lua.close()

print(f'skipped total: {skips}')