class StreamAggregator:
    def __init__(self, state: dict, streams: dict):
        self._state = state
        self._streams = streams

    @property
    def state(self) -> dict:
        state = {}
        for stream_id, stream_obj in self._streams.items():
            state[stream_id] = stream_obj.state
        return state

    @property
    def insert(self) -> dict:
        insert_dict = {}
        for stream in self._streams.values():
            stream_insert = stream.insert
            for table, records in stream_insert.items():
                if table in insert_dict:
                    insert_dict[table].extend(records)
                else:
                    insert_dict[table] = []
                    insert_dict[table].extend(records)
        return insert_dict

    @property
    def delete(self) -> dict:
        delete_dict = {}
        for stream in self._streams.values():
            stream_delete = stream.delete
            for table, records in stream_delete.items():
                if table in delete_dict:
                    delete_dict[table].extend(records)
                else:
                    delete_dict[table] = []
                    delete_dict[table].extend(records)
        return delete_dict

    @property
    def schema(self) -> dict:
        schema_dict = {}
        for stream in self._streams.values():
            stream_schema = stream.schema
            for table, schema in stream_schema.items():
                if table not in schema_dict:
                    schema_dict[table] = schema
        return schema_dict

    @property
    def has_more(self) -> bool:
        for stream in self._streams.values():
            if stream.has_more:
                return True
        return False

    @property
    def response(self) -> dict:
        return {
            "state": self.state,
            "insert": self.insert,
            "delete": self.delete,
            "schema": self.schema,
            "hasMore": self.has_more,
        }

    def sync(self) -> None:
        if self.has_more:
            for stream in self._streams.values():
                stream.sync()

    def reset(self) -> None:
        for stream in self._streams.values():
            stream.reset()
