def get_dict(data, attr_name):
    return {key: data[attr_name][key - 1] for key in range(1, len(data[attr_name]) + 1)}

