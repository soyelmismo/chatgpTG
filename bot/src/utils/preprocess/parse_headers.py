from ujson import loads, JSONDecodeError

def try_parse_json(value):
    try:
        return loads(value)
    except (JSONDecodeError, TypeError):
        return value

def parse_values_to_json(headers_dict):
    for key, value in headers_dict.items():
        headers_dict[key] = try_parse_json(value)
    return headers_dict