from dataclasses import dataclass
from .sqlite_adapt import fetch_data,QueryObject
from .logic import RegistryData, ConfigSetting


@dataclass
class Configurator:
    _groups:dict = None
    _settings:RegistryData = None
    _by_name:dict = None

    def __post_init__(self):
        self._groups = {}
        self._by_name = {}
        self._settings = RegistryData(150)
        qr = QueryObject(table='configs')
        res = fetch_data(qr,True)
        for s in res:
            # print(s)
            if s['group'] not in self._groups:
                self._groups[s['group']] = {}

            settconfig = {k:v for k,v in s.items() if k != "group"}
            setting = ConfigSetting()
            setting.from_db(settconfig)
            reg_id = self._settings.register(setting)
            self._groups[s['group']][reg_id] = setting.name
            self._by_name[reg_id]=setting.name

    @property
    def groups(self)->list:
        return [k for k in self._groups.keys()]

    def settings_by_group(self,name:str)->dict:
        out = {v:self._settings.by_id(k) for k,v in self._groups[name].items()}
        return out


    def setting_by_name(self,name:str)->ConfigSetting:
        out = None
        for k,v in self._by_name.items():
            if v == name:
                out = self._settings.registry[k]
        return out

Config = Configurator()
