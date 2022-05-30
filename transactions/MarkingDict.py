from collections.abc import MutableMapping, Mapping


class MarkingDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.access_count = {}
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        self.access_count[key] += 1
        return self.store[key]

    def __setitem__(self, key, value):
        if key not in self.access_count:
            self.access_count[key] = 0
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]
        del self.access_count[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __contains__(self, key):
        return key in self.store

    def __repr__(self):
        return '{store: ' + self.store.__str__() + '\naccess count: ' + self.access_count.__str__() + '}'

    def validate(self):
        validate = True
        for key, value in self.store.items():
            if isinstance(value, MarkingDict):
                validate = validate and value.validate()
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, MarkingDict):
                        validate = validate and item.validate()
        return validate and min(self.access_count.values()) > 0

    def not_used_keys(self, cur_path=''):
        paths = set([cur_path + key for key, access_count in self.access_count.items() if access_count == 0])
        for key, value in self.store.items():
            if isinstance(value, MarkingDict):
                paths = paths | value.not_used_keys(cur_path + key + '/')
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, MarkingDict):
                        paths = paths | item.not_used_keys(cur_path + key + '/')
        return paths


def create_deep_mraking_dict(dict_to_mark):
    for key, item in dict_to_mark.items():
        if isinstance(item, Mapping):
            new_val = create_deep_mraking_dict(item)
            dict_to_mark[key] = new_val
        elif isinstance(item, list):
            new_list = []
            for inner_item in item:
                if isinstance(inner_item, Mapping):
                    new_val = create_deep_mraking_dict(inner_item)
                    new_list.append(new_val)
                else:
                    new_list.append(inner_item)
            dict_to_mark[key] = new_list
    return MarkingDict(dict_to_mark)
