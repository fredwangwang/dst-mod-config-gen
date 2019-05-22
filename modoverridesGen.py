import glob
import os
import re
import sys

from lupa import LuaRuntime

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


class ModInfos:
    def __init__(self):
        self.modinfos = {}

    def load_from_existing_file(self, filepath):
        with open(filepath, "r", encoding="UTF-8") as inf:
            mod_overrides_str = inf.read()
        self.load_from_existing_str(mod_overrides_str)

    def load_from_existing_str(self, content: str):
        content = "function()\n" + content + "\nend"

        lua = LuaRuntime(unpack_returned_tuples=True)
        modinfos_func = lua.eval(content)
        modinfos_lua = modinfos_func()
        print(modinfos_lua)
        for modinfo in modinfos_lua.items():
            self.modinfos[modinfo[0]] = self._load_from_configs_entry(modinfo[1])

    def _load_from_configs_entry(self, entry):
        enabled = entry.enabled
        configs = dict(entry.configuration_options and entry.configuration_options.items() or ())
        print(enabled, configs)



class ModInfo:
    def __init__(self, name, configs, enabled=True):
        self.name = name
        self.configs = configs
        self.workshop_id = ""
        self.indent = "  "
        self.enabled = enabled

    # @staticmethod
    # def load_from_existing_lua_obj(entry):
    #     enabled = entry.enabled or False
    #

    def set_workshop_id(self, folder_name):
        self.workshop_id = folder_name

    def _sanitize_data(self, data):
        if isinstance(data, str):
            value = "\"" + data + "\""
        elif isinstance(data, bool):
            if data:
                value = "true"
            else:
                value = "false"
        else:
            value = data
        return value

    def _to_lua_string_configs_entry_options(self, options):
        rets = []
        for option in options:
            rets.append("-- description = %s, data = %s" % (option["description"], self._sanitize_data(option["data"])))
        return rets

    def _to_lua_string_configs_entry(self, entry):
        rets = []
        rets.append("-- %s" % (entry["label"] or entry["name"]))
        rets.extend(self._to_lua_string_configs_entry_options(entry["options"]))
        rets.append("[\"%s\"] = %s," % (entry["name"], self._sanitize_data(entry["default"])))
        return map(lambda x: self.indent + x, rets)

    def _to_lua_string_configs(self):
        rets = []
        if not self.configs:
            return []
        rets.append("configuration_options = {")
        for entry in self.configs:
            rets.extend(self._to_lua_string_configs_entry(entry))
        rets.append("},")
        return map(lambda x: self.indent + x, rets)

    def to_lua_string(self, indent="  "):
        self.indent = indent

        rets = []
        rets.append("-- %s" % self.name)
        rets.append("[\"%s\"] = { enabled = %s," % (self.workshop_id, self._sanitize_data(self.enabled)))
        rets.extend(self._to_lua_string_configs())
        rets.append("},")
        return "\n".join(map(lambda x: self.indent + x, rets))

    def __str__(self):
        return self.to_lua_string()


def parse_config_options(options_lua_iter):
    options = []
    for option_lua in options_lua_iter:
        option = {
            "description": option_lua.description,
            "data": option_lua.data
        }
        options.append(option)
    return options


def parse_modinfo_string(content: str):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(content)
    g = lua.globals()

    name = g.name
    configs = []
    if g.configuration_options:
        configs_lua = g.configuration_options.values()
        for config_lua in configs_lua:
            config = {
                "name": config_lua.name,
                "label": config_lua.label,
                "default": config_lua.default,
                "options": parse_config_options(config_lua.options.values())
            }
            configs.append(config)

    return ModInfo(name, configs)


def parse_modinfo_file(filepath: str):
    print("processing", filepath)
    workshop_id = os.path.basename(os.path.dirname(filepath))
    with open(filepath, "r", encoding='UTF-8', errors='ignore') as modinfo_file:
        # Health Info has invalid escape sequence in the string... sanitize it so lua interpreter
        modinfo_str = re.sub('(?<!\\\\)\\\\(?![ "ntr\\\\])', '', modinfo_file.read())
        with open(filepath + "mod", "w", encoding="UTF-8") as mdedfile:
            mdedfile.write(modinfo_str)
    mod_info = parse_modinfo_string(modinfo_str)
    mod_info.set_workshop_id(workshop_id)
    return mod_info.to_lua_string("    ")


def parse_mod_info_files(filepaths):
    rets = []
    rets.append("return {")
    for filepath in filepaths:
        rets.append(parse_modinfo_file(filepath))
    rets.append("}")
    return "\n".join(rets)


def get_all_modinfo(mod_root):
    return sorted(glob.glob(os.path.join(mod_root, "*", "modinfo.lua")))


def is_right_folder(dirpath):
    return os.path.isfile(os.path.join(dirpath, "modsettings.lua"))


if __name__ == "__main__":
    mod_root_folder = os.getcwd()

    if not is_right_folder(mod_root_folder):
        print("make sure you are only running this file inside mods folder")
        exit(1)

    with open("modoverrides.lua", "w", encoding="UTF-8") as outf:
        outf.write(parse_mod_info_files(get_all_modinfo(mod_root_folder)))

    ModInfos().load_from_existing_file("modoverrides.lua")
