import glob
import os
import re
import sys
from collections import OrderedDict

from lupa import LuaRuntime

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

indent = "    "


def sanitize_data(data):
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


class ModInfoConfig:
    def __init__(self, name=None, label=None, default=None, options=None):
        if options is None:
            options = []
        self.name = name
        self.label = label
        self.default = default
        self.options = options

    def __str__(self) -> str:
        return "\n".join(self.to_lua_string_parts())

    def _to_lua_string_config_options(self):
        rets = []
        for option in self.options:
            rets.append(
                "-- description = %s, data = %s" % (option["description"], sanitize_data(option["data"])))
        return rets

    def to_lua_string_parts(self):
        rets = []
        rets.append("-- %s" % (self.label or self.name))
        rets.extend(self._to_lua_string_config_options())
        rets.append("[\"%s\"] = %s," % (self.name, sanitize_data(self.default)))
        return rets

    def merge(self, other):
        self.name = self.name or other.name
        self.label = self.label or other.label
        self.default = self.default or other.default
        self.options = other.options or self.options
        return self

    @staticmethod
    def load_from_existing_overrides_options_item(entry):

        name = entry[0]
        default = entry[1]
        return ModInfoConfig(name=name, default=default)

    @staticmethod
    def load_from_existing_overrides_options_items(entries):
        return OrderedDict(
            map(lambda x: (x.name, x), map(ModInfoConfig.load_from_existing_overrides_options_item, entries)))

    @staticmethod
    def _parse_config_options(options_lua_iter):
        return list(map(lambda x: {
            "description": x.description,
            "data": x.data
        }, options_lua_iter))

    @staticmethod
    def load_from_config_lua(config_lua):
        return ModInfoConfig(
            name=config_lua.name,
            label=config_lua.label,
            default=config_lua.default,
            options=ModInfoConfig._parse_config_options(config_lua.options.values())
        )

    @staticmethod
    def load_from_configs_lua(configs_lua):
        return list(map(ModInfoConfig.load_from_config_lua, configs_lua))


class ModInfo:
    def __init__(self, name=None, configs=None, enabled=False):
        if configs is None:
            configs = OrderedDict()
        self.name = name
        self.configs = configs
        self.workshop_id = ""
        self.enabled = enabled

    def __str__(self):
        return "\n".join(self.to_lua_string_parts())

    def _set_workshop_id(self, folder_name):
        self.workshop_id = folder_name

    @staticmethod
    def load_from_modinfo_file(filepath: str):
        print("processing", filepath)
        workshop_id = os.path.basename(os.path.dirname(filepath))
        with open(filepath, "r", encoding='UTF-8', errors='ignore') as modinfo_file:
            # Health Info has invalid escape sequence in the string... sanitize it so lua interpreter
            modinfo_str = re.sub('(?<!\\\\)\\\\(?![ "ntr\\\\])', '', modinfo_file.read())
        mod_info = ModInfo.parse_modinfo_string(modinfo_str)
        mod_info._set_workshop_id(workshop_id)
        return mod_info

    @staticmethod
    def parse_modinfo_string(content: str):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(content)
        g = lua.globals()

        name = g.name
        configs = []
        if g.configuration_options:
            configs_lua = g.configuration_options.values()
            configs = ModInfoConfig.load_from_configs_lua(configs_lua)
        return ModInfo(name, OrderedDict(map(lambda x: (x.name, x), configs)))

    def merge(self, other):
        self.name = self.name or other.name
        self.workshop_id = self.workshop_id or other.workshop_id
        self.enabled = self.enabled or other.enabled

        if not other.configs:
            return
        if not self.configs:
            self.configs = OrderedDict()
        old_config = self.configs
        self.configs = other.configs
        for ock, ocv in old_config.items():
            if ock not in self.configs:
                # if the new configuration_options does not contain the specific option,
                # probably we shouldn't include it in the new config neither.
                # self.configs[ock] = ocv
                pass
            else:
                self.configs[ock] = ocv.merge(self.configs[ock])
                # self.configs[ock].merge(ocv)

    def _to_lua_string_configs(self):
        rets = []
        if not self.configs:
            return []
        rets.append("configuration_options = {")
        for entry in self.configs.values():
            rets.extend(entry.to_lua_string_parts())
        rets.append("},")
        return map(lambda x: indent + x, rets)

    def to_lua_string_parts(self):
        rets = []
        rets.append("-- %s" % self.name)
        rets.append("[\"%s\"] = { enabled = %s," % (self.workshop_id, sanitize_data(self.enabled)))
        rets.extend(self._to_lua_string_configs())
        rets.append("},")
        return map(lambda x: indent + x, rets)


class ModInfos:
    def __init__(self, modinfos=None):
        self.modinfos = modinfos or OrderedDict()

    @staticmethod
    def load_from_existing_overrides_file(filepath):
        if not os.path.isfile(filepath):
            return ModInfos()
        with open(filepath, "r", encoding="UTF-8") as inf:
            mod_overrides_str = inf.read()
        return ModInfos.load_from_existing_overrides_str(mod_overrides_str)

    @staticmethod
    def load_from_existing_overrides_str(content: str):
        content = "function()\n" + content + "\nend"

        lua = LuaRuntime(unpack_returned_tuples=True)
        modinfos_func = lua.eval(content)
        modinfos_lua = modinfos_func()
        modinfos = OrderedDict()
        for modinfo in modinfos_lua and modinfos_lua.items() or []:
            modinfos[modinfo[0]] = ModInfos._load_from_configs_entry(modinfo[1])
        return ModInfos(modinfos)

    @staticmethod
    def _load_from_configs_entry(entry):
        enabled = entry.enabled
        configs = ModInfoConfig.load_from_existing_overrides_options_items(
            entry.configuration_options and entry.configuration_options.items() or ())

        return ModInfo(configs=configs, enabled=enabled)

    def load_from_modinfo_file(self, modinfo_file):
        workshop_id = os.path.basename(os.path.dirname(modinfo_file))
        info = ModInfo.load_from_modinfo_file(modinfo_file)
        if workshop_id not in self.modinfos:
            self.modinfos[workshop_id] = info
        else:
            self.modinfos[workshop_id].merge(info)

    def load_from_modinfo_files(self, modinfo_files):
        list(map(self.load_from_modinfo_file, modinfo_files))

    def __str__(self):
        rets = []
        rets.append("return {")
        for x in self.modinfos.values():
            rets.extend(x.to_lua_string_parts())
        rets.append("}")
        return "\n".join(rets)


def get_all_modinfo(mod_root):
    return sorted(glob.glob(os.path.join(mod_root, "*", "modinfo.lua")))


def is_right_folder(dirpath):
    return os.path.isfile(os.path.join(dirpath, "modsettings.lua"))


if __name__ == "__main__":
    mod_root_folder = os.getcwd()
    modoverrides_path = os.path.join(mod_root_folder, "modoverrides.lua")

    if not is_right_folder(mod_root_folder):
        print("make sure you are only running this file inside mods folder")
        exit(1)

    infos = ModInfos.load_from_existing_overrides_file(modoverrides_path)
    infos.load_from_modinfo_files(get_all_modinfo(mod_root_folder))
    with open("modoverrides.lua", "w", encoding="UTF-8") as outf:
        outf.write(str(infos))
