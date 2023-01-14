--#region Filters
WEAPON_MIN_RARITY = 3 -- 1 star to 5 star
WEAPON_MIN_LEVEL = 60 -- lvl 1 to lvl 90
WEAPON_MIN_ASCENSION = 0 -- 0 to 6, disambiguate 80/80 from 80/90 etc.

ARTIFACT_MIN_RARITY = 4 -- 1 star to 5 star
ARTIFACT_MIN_LEVEL = 16 -- lvl 0 to lvl 20

INCLUDE_MATERIALS = true --for seelie.me
--#endregion

local avatar_names = require("data.avatar_names")
local weapon_table = require("data.weapons")
local artifact_table = require("data.artifacts")
local fight_props = require("data.fight_props")
local material_names = require("data.material_names")

local player_store, avatar_data
local ownership_table = {}

local epsilon = 2^-52
local function round(num) --https://stackoverflow.com/a/58411671 why lua why
    local ofs = 2^52
    if math.abs(num) > ofs then
      return num
    end
    return num < 0 and num - ofs + ofs or num + ofs - ofs
  end

local function parse_data()
    if not player_store or not avatar_data then return end

    local characters = ""
    for name, avatar in pairs(avatar_data) do
        local prop_map = avatar:field("prop_map"):value():get()
        local level = prop_map[4001]:get():field("val"):value():get()
        local ascension = prop_map[1002]:get():field("val"):value():get()

        local constellation = #avatar:field("talent_id_list"):value():get()
        local talent_map = avatar:field("skill_level_map"):value():get()
        local tkeys, talents = {}, {}

        for k in pairs(talent_map) do table.insert(tkeys, k) end
        table.sort(tkeys, function(k1, k2) --these exceptions are fucked up ik
            if name == "KamisatoAyaka" then return k1 > k2 end
            return k1 < k2 end)
        for i, k in ipairs(tkeys) do talents[i] = talent_map[k]:get() end
        local skill_index = name == "KamisatoAyaka" and 3 or 2
        local burst_index = name == "KamisatoAyaka" and 2 or (name == "Mona" and 4 or 3) --why mihoyo why
        --notes: everyone else has talent IDs in ascending order, correspoding to auto, skill and burst respectively
        --EXCEPT Ayaka and Mona who both have 4 talents instead of the usual 3 (their special dashes)
        --and Ayaka's are in descending order, corresponding to auto, BURST, SKILL, dash, 
        --while Mona's are in ascending order, corresponding to auto, skill, DASH, burst
        --hopefully they're the only exceptions, I'm just too lazy to map out skill depots though I really should...

        local avatar_txt = (string.len(characters) > 0 and ",{" or "{")
        .. '"key":"' .. name .. '","level":' .. level
        .. ',"constellation":' .. constellation
        .. ',"ascension":' .. ascension
        .. ',"talent":{'
            .. '"auto":' .. talents[1]
            .. ',"skill":' .. talents[skill_index]
            .. ',"burst":' .. talents[burst_index]
        .. "}}"
        characters = characters .. avatar_txt
    end

    local weapon_count = 0
    local artifact_count = 0
    local material_count = 0
    local furniture_count = 0
    local filtered = 0

    local weapons = ""
    local artifacts = ""
    local materials = ""
    for guid, item in pairs(player_store) do
        local id = item:field("item_id"):value():get()

        local furniture = item:field("furniture"):value():get()
        if furniture:field("count"):value():get() > 0 then
            furniture_count = furniture_count + 1
            goto continue 
        end

        local material = item:field("material"):value():get()
        local count = material:field("count"):value():get()
        if count > 0 then
            local key = material_names[id]
            if key and INCLUDE_MATERIALS then
                local material_txt = (string.len(materials) > 0 and ',"' or '"')
                .. key .. '":' .. count
                materials = materials .. material_txt
                material_count = material_count + 1
                goto continue
            end
        end

        local location = ownership_table[guid] or ""
        local equip = item:field("equip"):value():get()
        local lock = equip:field("is_locked"):value():get() and "true" or "false"

        local weapon = equip:field("weapon"):value():get()
        local weapon_lvl = weapon:field("level"):value():get()
        
        if weapon_lvl >= math.max(WEAPON_MIN_LEVEL, 1) then
            local weapon_data = weapon_table[id]
            local ascension = weapon:field("promote_level"):value():get()

            if weapon_data and weapon_data.rarity >= WEAPON_MIN_RARITY and ascension >= WEAPON_MIN_ASCENSION then
                local affix = weapon:field("affix_map"):value():get()
                local k, r = next(affix)
                local refinement = (k and r:get() or 0) + 1

                local weapon_txt = (string.len(weapons) > 0 and ",{" or "{")
                .. '"key":"' .. weapon_data.key .. '","level":' .. weapon_lvl
                .. ',"ascension":' .. ascension .. ',"refinement":' .. refinement
                .. ',"location":"' .. location .. '","lock":' .. lock .. '}'
                weapons = weapons .. weapon_txt
                weapon_count = weapon_count + 1
                goto continue
            end
        end

        local artifact = equip:field("reliquary"):value():get()
        local artifact_lvl = artifact:field("level"):value():get()

        if artifact_lvl >= math.max(ARTIFACT_MIN_LEVEL + 1, 1) then
            local artifact_data = artifact_table[id]
            if artifact_data and artifact_data.rarity >= ARTIFACT_MIN_RARITY then
                local main_stat = fight_props[artifact:field("main_prop_id"):value():get()]
                local prop_list = artifact:field("append_prop_id_list"):value():get()
                local skeys, substats = {}, {}

                for _, p in ipairs(prop_list) do
                    local prop = fight_props[p:get()]
                    if not substats[prop.key] then
                        substats[prop.key] = 0
                        table.insert(skeys, prop.key)
                    end
                    substats[prop.key] = substats[prop.key] + prop.value
                end

                local artifact_txt = (string.len(artifacts) > 0 and ",{" or "{")
                .. '"setKey":"' .. artifact_data.set .. '","slotKey":"' .. artifact_data.slot
                .. '","level":' .. artifact_lvl - 1 .. ',"rarity":' .. artifact_data.rarity
                .. ',"mainStatKey":"' .. main_stat .. '","location":"' .. location
                .. '","lock":' .. lock .. ',"substats":['

                for i, key in ipairs(skeys) do
                    local value = substats[key]
                    if string.sub(key, -1) == "_" then --magic % rounding formula stolen from Iridium idfk why it has to be this way
                        value = round((value * 100 + epsilon + 0.0001) * 10) / 10 --why mihoyo why
                    else value = round(value) end
                    local substat = (i > 1 and ",{" or "{")
                    .. '"key":"' .. key .. '","value":' .. value .. "}"
                    artifact_txt = artifact_txt .. substat
                end

                artifact_txt = artifact_txt .. "]}"
                artifacts = artifacts .. artifact_txt
                artifact_count = artifact_count + 1
                goto continue
            end
        end

        filtered = filtered + 1
        ::continue::
    end

    print("Weapons: " .. weapon_count)
    print("Artifacts: " .. artifact_count)
    print("Materials: " .. material_count)
    print("Furnitures: " .. furniture_count)
    print("Filtered: " .. filtered)
    
    local good_ass_rip = '{"format":"GOOD","version":1,"source":"GOOD-ASS-Ripper",'
    .. '"characters":[' .. characters .. '],"weapons":[' .. weapons
    .. '],"artifacts":[' .. artifacts .. '],"materials":{' .. materials
    .. '}}'

    local file = assert(io.open("GOOD-ASS-Rip.json", "w"))
    if file then
        file:write(good_ass_rip)
        file:flush()
        file:close()
        print("Export success! See GOOD-ASS-Rip.json")
    end
end

function on_filter(packet)
    local pid = packet:mid()

    --PlayerStoreNotify
    if pid == 679 then
        if player_store then return true end
        local node = packet:content():node()
        local list = node:field("item_list"):value():get()
        print("Items: " .. #list)
        player_store = {}
        for _, i in ipairs(list) do
            local item = i:get()
            local guid = item:field("guid"):value():get()
            player_store[guid] = item
        end
        parse_data()
        return true

    --AvatarDataNotify
    elseif pid == 1607 then
        if avatar_data then return true end
        local node = packet:content():node()
        local list = node:field("avatar_list"):value():get()
        print("Avatars: " .. #list)
        avatar_data = {}
        for _, a in ipairs(list) do
            local avatar = a:get()
            local id = avatar:field("avatar_id"):value():get()
            -- Print error if new character is not defined in the table
            if avatar_names[id] == nil then
                print("Unknown avatar id " .. id)
            end
            local name = avatar_names[id]
            local equips = avatar:field("equip_guid_list"):value():get()
            for _, e in ipairs(equips) do
                ownership_table[e:get()] = name
            end
            avatar_data[name] = avatar
        end
        parse_data()
        return true
    end

    return false
end
