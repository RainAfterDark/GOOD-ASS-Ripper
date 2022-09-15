from pathlib import Path
import json

path = Path(__file__).parent

prop_names = {
    "FIGHT_PROP_HP": "hp",
    "FIGHT_PROP_HP_PERCENT": "hp_",
    "FIGHT_PROP_ATTACK": "atk",
    "FIGHT_PROP_ATTACK_PERCENT": "atk_",
    "FIGHT_PROP_DEFENSE": "def",
    "FIGHT_PROP_DEFENSE_PERCENT": "def_",
    "FIGHT_PROP_CHARGE_EFFICIENCY": "enerRech_",
    "FIGHT_PROP_ELEMENT_MASTERY": "eleMas",
    "FIGHT_PROP_CRITICAL": "critRate_",
    "FIGHT_PROP_CRITICAL_HURT": "critDMG_",
    "FIGHT_PROP_HEAL_ADD": "heal_",
    "FIGHT_PROP_FIRE_ADD_HURT": "pyro_dmg_",
    "FIGHT_PROP_ELEC_ADD_HURT": "electro_dmg_",
    "FIGHT_PROP_ICE_ADD_HURT": "cryo_dmg_",
    "FIGHT_PROP_WATER_ADD_HURT": "hydro_dmg_",
    "FIGHT_PROP_WIND_ADD_HURT": "anemo_dmg_",
    "FIGHT_PROP_ROCK_ADD_HURT": "geo_dmg_",
    "FIGHT_PROP_GRASS_ADD_HURT": "dendro_dmg_",
    "FIGHT_PROP_PHYSICAL_ADD_HURT": "physical_dmg_"  
}

prop_table = {}

f_lua = open(path / "fight_props.lua", "w")
f_lua.write("local fight_props = {\n")

f_mprop_excel = open(path / "ReliquaryMainPropExcelConfigData.json")
mprop_data = json.load(f_mprop_excel)
f_mprop_excel.close()

for i in mprop_data:
    if i["propType"] not in prop_names: continue
    f_lua.write(f'\t[{i["id"]}] = "{prop_names[i["propType"]]}",\n')

f_affix_excel = open(path / "ReliquaryAffixExcelConfigData.json")
affix_data = json.load(f_affix_excel)
f_affix_excel.close()

for i in affix_data:
    if i["propType"] not in prop_names: continue
    data = f'key = "{prop_names[i["propType"]]}", value = {i["propValue"]}'
    f_lua.write(f'\t[{i["id"]}] = {{{data}}},\n')

f_lua.write("}\nreturn fight_props")
f_lua.close()