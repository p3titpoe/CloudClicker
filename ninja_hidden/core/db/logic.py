from dataclasses import dataclass,field
from enum import Enum
from json import loads,dumps

class ConfigTypes(Enum):
    INT = int
    STR = str
    JSON_DICT = dict
    JSON_LIST = dict
    URL = str
    LINK = str

    @classmethod
    def by_name(cls, name: str):
        att = getattr(cls, name)
        return att


@dataclass(repr=False)
class ConfigSetting:
    name:str = ""
    _value:str = ""
    _type:ConfigTypes = None
    _id:int = 0
    _value_changed:bool = False

    def __repr__(self):
        text= "ConfigSetting("
        text += (f"name: {self.name}, "
                 f"type: {self._type.value}, "
                 f"value: {self._value}"
                 )
        return text

    @property
    def value_changed(self)->bool:
        return self._value_changed

    @property
    def id (self)->int:
        return self._id

    @property
    def value(self):
        if 'JSON' not in self._type.name:
            out = self._type.value(self._value)
        else:
            out = loads(self._value)
        return out

    @value.setter
    def value(self, val):
        if 'JSON' not in self._type.name:
            if isinstance(val,self._type.value):
                self._value = val
                self._value_changed = True
            else:
                print(f"Wrong value for Setting: {self.name}")
        else:
            try:
                if isinstance(val,self._type.value):
                    js = dumps(val)
                    self._value = js
                    self._value_changed = True
            except:
                print("Not convertible to Json")

    @property
    def typ(self):
        return self._type.value

    def from_db(self,data:dict)->None:
        for k,v in data.items():
            val = v
            if k == '_type':
                val = ConfigTypes.by_name(v.upper())
            self.__dict__[k] = val
        self._id = data['id']

    def to_list(self)->list:
        out = []
        if self._type.name == "JSON_DICT":
            vals:dict = self.value
            out = [v for k,v in vals.items()]
        if self._type.name == "JSON_LIST":
            out = self.value
        return out

    def to_db(self)->dict:
        out = {k:v for k,v in self.__dict__.items() if k != "_id"}
        out['id'] = self._id
        return out

    def save(self):
        return self.to_db()



##Base Data Classes
@dataclass(repr=False)
class BaseData:
    """
        Basic obj class derived from dataclass

        Uses a custom __repr__ method. \n
        Built in serialization of the attributes, sorts out protected (__) and shows private(_) as normal attribute\n
        Can be initialized with a key-value dictionary for data-representation. Keys will be set as attribute for
        . accessing style.\n
        Built in save method for convenience

        PARAMETERS:
            - None

        RETURNS:
            - BaseData object

    """
    def __repr__(self):
        data = self.keypairs
        out = f'{self.__class__.__name__} ('
        for k, v in data.items():
            out += f'{k} = {v}, '
        out = out[:-2]
        out += f')'
        return out

    def _keypairs(self,show_private: bool = True) -> dict:
        """
            Creates a dict based on the inner .__dict__ by filtering out protected(__) attributes.

            Private attributes will be printed without capitalized (Default)
            Call __keypairs(show_private=False) to omit the private fields

            PARAMETERS:
                - show_private: Bool = if private fields should be shown.

            RETURNS:
                - dict = output of _keypairs
        """
        own_fields: dict = self.__dict__
        outd = {}
        for k, v in own_fields.items():
            f_name = k
            if k.find("__") == 0:
                pass
            else:
                if k.find("_") == 0 and show_private:
                    spl = k.split("_")
                    f_name = spl[-1]
                outd[f_name] = v
        return outd

    @property
    def keypairs(self ) -> dict:
        """
            sorts out protected (__) and shows private(_) as normal attribute from members

            PARAMETERS:
                 -None

            RETURNS:
                - dict = name:values of fields
        """
        return self._keypairs()

    def init_from_db(self, db_res: dict) -> None:
        """
            Initialize from a dictionnary
            Practical for on the fly datamodel creation or extension of attributes

            PARAMETERS:
                - db_res: dictionary - Dict with datamodel

            RETURNS:
                - None

        """
        for k, v in db_res.items():
            setattr(self, k, v)

    def save(self)->dict:
        """
            Convenience method for _keypairs

            .. warning::
                !!Might change in future!!

            PARAMETERS:
                - None

            RETURNS:
                - dict = _keypairs output

        """
        return self._keypairs()


@dataclass(repr=False)
class QueryObject(BaseData):
    """
        Simple SQLite SELECT query construction class.\n
        TODO Implement LEFT Join.

        .. note::
            __check_search now ouputs the operator

        .. tip::
            search_operator keys
                - "="      -> **= $search**
                - "LIKE"   -> **$search%**
                - "PRELIKE"-> **%$search**
                - "DLIKE"  -> **%$search%**
                - "NOTL"  -> NOT LIKE **$search%**
                - default == **"="**

        .. tip::
            order_modes keys
                - ASC
                - DESC

        PARAMETERS:
            - table: str = default= None
            - columns: list[str]| str  = default = None
            - search_column: list[str] | str | None = default = None
            - list[str] | str | None = default = None
            - search_operator: list[str] | str = default = "="
            - sql_function: list[str] | None = default = None
            - list[str] | None = default = None
            - order_by: str | None = default = None
            - order_mode: str = default='DESC'
            - limit: int | None = default = None

        RETURNS:
            - JT_Query object


        SIMPLE USAGE
        ------------

        .. code-block::text

            JT_Query("Foo").query

            -> SELECT * FROM Foo WHERE

            JT_Query(table="Foo", columns=["a","b","c"] ).query
            -> SELECT a,b,c FROM Foo WHERE 1

            JT_Query(table="Foo", columns=["a","b","c"], search_column="bar",search_column_value = 42).query
            -> SELECT a,b,c FROM Foo WHERE bar = 42


            JT_Query(
                    table="Foo",
                    sql_function = ["SUM(a)","MAX(b)"],
                    sql_function_as = ["total","maximum"]
                    search_column="bar",
                    search_column_value = 42,
                    search_operator = "=",
                    ).query
                -> SELECT SUM(a) as total ,MAX(a) as maximum FROM Foo WHERE bar=42


            JT_Query(
                    table="Foo",
                    columns="b",
                    search_column=["bar","fud"],
                    search_column_value = [42,2024),
                    search_operator = ["=","LIKE"],
                    order_by = "a",
                    order_mode = "ASC",
                    limit = [5,10]
                    ).query
                -> SELECT b FROM Foo WHERE bar=42 AND fud LIKE "2024%" ORDER BY a ASC LIMIT 5,10


            JT_Query(
                    table="Foo",
                    sql_function = "DISTINCT(a)",
                    sql_function_as = "aa",
                    columns="b",
                    search_column=["bar","fud"],
                    search_column_value = [42,2024),
                    search_operator = ["=","LIKE"],

                    order_by = "a",
                    order_mode = "DESC",
                    limit = 5
                    ).query
                -> SELECT DISTINCT(a) as aa,b FROM Foo WHERE bar=42 AND fud LIKE "2024%" ORDER BY a DESC LIMIT 0,5

    """
    #: Name of the table
    table: str | None = field(default=None)
    #: Columns to fetch. If > 1, use a list.
    columns: list[str] | None = field(default=None)
    #: Column(s) to to search in. If > 1, use a list.
    search_column: list[str] | str | None = field(default=None)
    #: Values for the search. If > 1, use a list. Values and columns will be matched by index
    search_column_value: list[str] | str | None = field(default=None)
    #: Operators to use. If > 1, use a list. Operators and searches will be matched by index
    search_operator: list[str] | str = field(default="=")
    #: Sqlfunction have to written as a string. If > 1, use a list.
    sql_function: list[str] | None = field(default=None)
    #: Aliases for sqlfunctions. If > 1, use a list. Aliases and functions will be matched by index
    sql_function_as: list[str] | None = field(default=None)
    #: Column to order by
    order_by: str | None = field(default=None)
    #: Either ASC or DESC. Default == DESC
    order_mode: str = field(default='DESC')
    #: Either int (end) or tuple(start, end)
    limit: int | None = field(default=None)

    def __check_sql_function(self,ssql:str)->str:
        if self.sql_function is not None:
            ssql = ''
            if isinstance(self.sql_function,str):
                self.sql_function = [self.sql_function]
                self.sql_function_as = [self.sql_function_as]

            for i, sq in enumerate(self.sql_function):
                ssql += f'{sq} '
                if self.sql_function_as is not None:
                    ssql += f'as {self.sql_function_as[i]},'
            ssql = ssql[:-1]
        return ssql

    def __check_columns(self,ssql:str)->str:
        if self.columns is not None:
            pre: str = f",{self.table}."
            if self.sql_function is None:
                ssql = f"{self.table}."
            else:
                ssql += pre
            ssql += f'{pre.join(self.columns) }'
        return ssql

    def __check_search(self)->str:
        sql = ""
        if self.search_column is not None:
            op_modes = {"=": "{}",
                        "LIKE": "'{}%'",
                        "DLIKE": "'%{}%'",
                        "PRELIKE": "'%{}'",
                        "NOT LIKE": "'%{}'",}
            tmp_oplist = []
            tmp_collist = []
            tmp_vallist = []
            if isinstance(self.search_column, str):
                tmp_oplist.append(self.search_operator)
                tmp_vallist.append(self.search_column_value)
                tmp_collist.append(self.search_column)

            if isinstance(self.search_column, list):
                tmp_oplist = self.search_operator
                tmp_vallist = self.search_column_value
                tmp_collist = self.search_column
            cnt = len(tmp_collist)
            sub = ""
            for i, col in enumerate(tmp_collist):
                op_trans = tmp_oplist[i]
                if i == 0:
                    sub = f'WHERE '
                else:
                    sub = f"AND "
                if op_trans != "=":
                    op_trans = "LIKE"
                sql += f'{sub}{self.table}.{col} {op_trans} {op_modes[tmp_oplist[i]].format(tmp_vallist[i])} '
            # if self.search_operator == 'LIKE':
            #     operator = f'LIKE "{self.search_column_value}%"'
            # sql += f'WHERE {self.table}.{self.search_column} {operator} '

        else:
            sql += f'Where 1 '
        return sql

    def __check_orderlimits(self) -> str:
        sql = ""
        if self.order_by is not None:
            sql += f'ORDER BY {self.table}.{self.order_by} {self.order_mode} '
        # else:
        #     sql += f'ORDER BY {self.table}.{self.columns[0]} {self.order_mode} '

        if self.limit is not None:
            start = 0
            end = 1
            if isinstance(self.limit,int):
                end = self.limit
            else:
                start = self.limit[0]
                end = self.limit[1]
            sql += f'LIMIT {start},{end}'

        return sql

    def __new_query_func(self):
        if self.table is None:
            raise AttributeError('Table is none')
        sql = f'SELECT '
        ssql = '*'
        ssql = self.__check_sql_function(ssql)
        ssql = self.__check_columns(ssql)
        sql += ssql
        sql += f' FROM {self.table} '
        sql += self.__check_search()
        sql += self.__check_orderlimits()
        return sql

    @property
    def query(self) -> str:
        """
            The computed query.

            PARAMETERS:
                - None

            RETURNS:
                - str = the computed query string

        """
        return self.__new_query_func()

@dataclass(repr=False)
class RegistryData(BaseData):
    """
        Creates a dictionnary with register from 0 to  given max_len and
        manages the data inside these registers.
        \n
        .. tip::
            LOGICAL COMPONENTS:
                registry :dict(read-only)
                    Represents the initial registry where data is stored

                booked: list(read-only)
                    A list holding registry id's in which data is stored (which are booked)

                free: list(read-only)
                    A list containing empty registry id's

        PARAMETERS:
            - max_len: int = length of the registry

        RETURNS:
            - Registry Object


    """
    _registry: dict[int:tuple] = field(init=False, default_factory=dict)
    _booked: list[int] = field(init=False, default_factory=list)
    _free: list[int] = field(init=False, default_factory=list)
    #: Length of the register, eg how many rooms
    max_len: int = field(default=70)

    def __post_init__(self) -> None:
        #Create the Registry
        self._registry = {nr: None for nr in range(0, self.max_len)}
        self._make_lists()

    def _make_lists(self) -> None:
        """
            Creates the _free and booked list

            PARAMETERS:
                - None

            RETURNS:
                - None
        """
        self._booked = [k for k, v in self._registry.items() if v is not None]
        self._free = [k for k, v in self._registry.items() if v is None]
        self._post_lists()

    @property
    def booked(self) -> list[int]:
        """Booked registers (ro)"""
        return self._booked

    @property
    def free(self) -> list[int]:
        """Free registers (ro)"""
        return self._free

    @property
    def registry(self) -> dict:
        """Access to the registry (ro)"""
        return self._registry

    def by_id(self,regid:int)->any:
        return self._registry[regid]

    def register(self, reg) -> int:
        """
        Insert data into first register from the free list.\n

        .. tip::
            Should be overridden by childs to accomodate for custom logic
            This is the simplest form of register transaction

        .. warning::
            **Make sure to return the registry id!**

        PARAMETERS:
            - **kwargs

        RETURNS:
            - int = Registry Id

        """
        reg_id = self.free[0]
        self._registry[reg_id] = reg
        self._make_lists()
        return reg_id

    def checkout(self, reg_id: int) -> any:
        """
            Remove data from registry

            PARAMETERS:
                - reg_id: int = Registry id

            RETURNS:
                - any = Data from given registry

        """
        out = self._registry[reg_id]
        self._registry[reg_id] = None
        self._make_lists()
        return out

    def _post_lists(self):
        pass