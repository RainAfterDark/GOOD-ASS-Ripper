from pathlib import Path
import re, json

data_path = Path(__file__).parent
resource_path = Path("") # provide resources directory path here
bin_path = resource_path / "BinOutput\\"
excel_path = resource_path / "ExcelBinOutput\\"
textmap_path = resource_path / "TextMap\\TextMapEN.json"

def main():
    with open(textmap_path, encoding="utf-8") as f:
        textmap_data = json.load(f)
    gen_artifact_data(textmap_data)
    gen_weapon_data(textmap_data)
    gen_material_names(textmap_data)
    gen_fight_props()

def PascalCase(str): # why genshin optimizer why
    return re.sub(" ", "", re.sub("[^A-Za-z0-9 ]+", "", re.sub("-", " ", str)).title())

def gen_artifact_data(textmap_data):
    slot_names = {
        "EQUIP_BRACER": "flower",
        "EQUIP_NECKLACE": "plume",
        "EQUIP_SHOES": "sands",
        "EQUIP_RING": "goblet",
        "EQUIP_DRESS": "circlet"
    }

    affix_table, set_table = {}, {}
    artifacts = 0

    with open(excel_path / "EquipAffixExcelConfigData.json") as f:
        for i in json.load(f):
            hash = str(i["nameTextMapHash"])
            if hash not in textmap_data: continue
            affix_table[i["id"]] = textmap_data[hash]
        
    with open(excel_path / "ReliquarySetExcelConfigData.json") as f:
        for i in json.load(f):
            if "EquipAffixId" not in i: continue
            affix_id = i["EquipAffixId"]
            set_table[i["setId"]] = affix_table[affix_id]

    with open(excel_path / "ReliquaryExcelConfigData.json") as f:
        with open(data_path / "artifacts.lua", "w", encoding="utf-8") as f_lua:
            f_lua.write("local artifacts = {\n")
            for i in json.load(f):
                hash = str(i["nameTextMapHash"])
                if hash not in textmap_data: continue
                name = PascalCase(textmap_data[hash])
                set = ""
                if "setId" in i and i["setId"] in set_table:
                    set = PascalCase(set_table[i["setId"]])
                slot = slot_names[i["equipType"]]
                data = ('{\n' +
                f'\t\tname = "{name}",\n' +
                f'\t\tset = "{set}",\n' +
                f'\t\tslot = "{slot}",\n' +
                f'\t\trarity = {i["rankLevel"]}\n' +
                '\t}')
                artifacts += 1
                f_lua.write(f'\t[{i["id"]}] = {data},\n')  
            f_lua.write("}\nreturn artifacts")
    print(f"Generated {artifacts} artifacts")

def gen_weapon_data(textmap_data):
    weapons = 0
    with open(excel_path / "WeaponExcelConfigData.json") as f:
        with open(data_path / "weapons.lua", "w", encoding="utf-8") as f_lua:
            f_lua.write("local weapons = {\n")
            for i in json.load(f):
                hash = str(i["nameTextMapHash"])
                if hash not in textmap_data: continue
                key = PascalCase(textmap_data[hash])
                data = f'{{\n\t\tkey = "{key}",\n\t\trarity = {i["rankLevel"]}\n\t}}'
                weapons += 1
                f_lua.write(f'\t[{i["id"]}] = {data},\n')
            f_lua.write("}\nreturn weapons")
    print(f"Generated {weapons} weapons")

def gen_material_names(textmap_data):
    materials = 0
    with open(excel_path / "MaterialExcelConfigData.json") as f:
        with open(data_path / "material_names.lua", "w", encoding="utf-8") as f_lua:
            f_lua.write("local material_names = {\n")
            for i in json.load(f):
                hash = str(i["nameTextMapHash"])
                if hash not in textmap_data or not PascalCase(textmap_data[hash]): continue
                materials += 1
                f_lua.write(f'\t[{i["id"]}] = "{PascalCase(textmap_data[hash])}",\n')
            f_lua.write("}\nreturn material_names")
    print(f"Generated {materials} materials")

def gen_fight_props():
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
    fight_props = 0

    with open(data_path / "fight_props.lua", "w") as f_lua:
        f_lua.write("local fight_props = {\n")

        with open(excel_path / "ReliquaryMainPropExcelConfigData.json") as f:
            for i in json.load(f):
                if i["propType"] not in prop_names: continue
                fight_props += 1
                f_lua.write(f'\t[{i["id"]}] = "{prop_names[i["propType"]]}",\n')

        with open(excel_path / "ReliquaryAffixExcelConfigData.json") as f:
            for i in json.load(f):
                if i["propType"] not in prop_names: continue
                data = f'key = "{prop_names[i["propType"]]}", value = {i["propValue"]}'
                fight_props += 1
                f_lua.write(f'\t[{i["id"]}] = {{{data}}},\n')
        
        f_lua.write("}\nreturn fight_props")
    print(f"Generated {fight_props} fight props")

if __name__ == "__main__": main()