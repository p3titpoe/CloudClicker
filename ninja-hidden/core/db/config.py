from dataclasses import dataclass
from .sqlite_adapt import fetch_data,update_data,QueryObject
from .logic import RegistryData, ConfigSetting

@dataclass
class ConfiguratorGroup:
    _lib:dict=None

    def __post_init__(self):
        self._lib = {}

    @property
    def settings(self)->dict:
        return self._lib

    def add_setting(self,config:ConfigSetting)->None:
        if config.name not in  self._lib:
            self._lib[config.name] = config

    def save(self):
        for k,cf in self._lib.items():
            if cf.value_changed:
                data = cf.save()
                update_data('configs',data)


@dataclass
class Configurator:
    _groups:dict = None
    _settings:RegistryData = None
    _by_name:dict = None

    def __post_init__(self):
        self._groups:dict[str:ConfiguratorGroup] = {}
        self._by_name = {}
        self._settings = RegistryData(150)
        qr = QueryObject(table='configs')
        res = fetch_data(qr,True)
        for s in res:
            # print(s)
            if s['group'] not in self._groups:
                self._groups[s['group']] = ConfiguratorGroup()

            settconfig = {k:v for k,v in s.items() if k != "group"}
            setting = ConfigSetting()
            setting.from_db(settconfig)
            reg_id = self._settings.register(setting)
            self._groups[s['group']].add_setting(setting)
            self._by_name[reg_id]=setting.name

    @property
    def groups(self)->list:
        return [k for k in self._groups.keys()]

    def settings_by_group(self,name:str)->ConfiguratorGroup:
        return self._groups[name]

    def setting_by_name(self,name:str)->ConfigSetting:
        out = None
        # print(name)
        for k,v in self._by_name.items():
            if v == name:
                out = self._settings.registry[k]
        return out

Config = Configurator()
