class Table:
    def __init__(self, primary_key=["id"]):
        self.insert = []
        self.delete = []
        self._primary_key = primary_key

    def insert_record(self, record: dict) -> None:
        self.insert.append(record)

    def insert_records(self, records: list) -> None:
        self.insert.extend(records)

    def delete_record(self, record: dict) -> None:
        self.delete.append(record)

    def delete_records(self, records: list) -> None:
        self.delete.extend(records)

    @property
    def primary_key(self) -> dict:
        return {"primary_key": self._primary_key}


class Stream:
    def __init__(self, state: dict, tables: dict):
        self._state = state or {**self.default_state(), **{"has_more": True}}
        self._tables = tables

    @property
    def state(self) -> dict:
        return self._state

    @property
    def insert(self) -> dict:
        insert = {}
        for table_name, table_obj in self._tables.items():
            insert[table_name] = table_obj.insert
        return insert

    @property
    def delete(self) -> dict:
        delete = {}
        for table_name, table_obj in self._tables.items():
            delete[table_name] = table_obj.delete
        return delete

    @property
    def schema(self) -> dict:
        schema = {}
        for table_name, table_obj in self._tables.items():
            schema[table_name] = table_obj.primary_key
        return schema

    @property
    def has_more(self) -> bool:
        try:
            return self._state["has_more"]
        except:
            raise KeyError(f"has_more missing from the state of {type(self)}")

    def sync(self) -> None:
        if self.has_more:
            self.get_records()

    def reset(self) -> None:
        self._state = {**self.reset_state(), **{"has_more": True}}

    def get_records(self) -> None:
        raise NotImplementedError(f"get_records() not implemented for {type(self)}")

    def reset_state(self) -> dict:
        raise NotImplementedError(f"reset_state() not implemented for {type(self)}")

    def default_state(self) -> None:
        raise NotImplementedError(f"default_state() not implemented for {type(self)}")

    def _get_table(self, table_name: str) -> Table:
        try:
            return self._tables[table_name]
        except:
            raise KeyError(f"Invalid table name for {type(self)}")

    def _insert_record(self, table_name: str, record: dict) -> None:
        table = self._get_table(table_name)
        table.insert_record(record)

    def _insert_records(self, table_name: str, records: list) -> None:
        table = self._get_table(table_name)
        table.insert_records(records)

    def _delete_record(self, table_name: str, record: dict) -> None:
        table = self._get_table(table_name)
        table.delete_record(record)

    def _delete_records(self, table_name: str, records: list) -> None:
        table = self._get_table(table_name)
        table.delete_records(records)
