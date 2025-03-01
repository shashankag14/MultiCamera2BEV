import yaml


def yaml_to_namespace(yaml_file):
    """Loads a YAML file and converts its content into a SimpleNamespace.

    Args:
        yaml_file (String): The path to the YAML file.

    Returns:
        SimpleNamespace:
            A SimpleNamespace object representing the YAML content.
    """
    try:
        with open(yaml_file, "r") as file:
            config_dict = yaml.safe_load(file)
    except FileNotFoundError:
        print(
            f"Warning: '{yaml_file}' not found.")
    return config_dict
