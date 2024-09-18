import yaml


def load_yaml_file(file_path):
    """
    Loads a YAML file and returns its content as a Python dictionary.

    Parameters
    ----------
    file_path : str
        The path to the YAML file.

    Returns
    -------
    dict
        The content of the YAML file as a Python dictionary.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data
