import configparser
import os

def load_config():
    paths = [os.path.expanduser('~/.ghot')]
    if os.path.exists('.ghot'):
        paths.append(os.path.abspath('.ghot'))

    config = configparser.ConfigParser(interpolation=None)
    config.read(paths)
    return config


def apply_config_defaults(parser, config):
    def set_str(default, section, key):
        if config.has_option(section, key):
            parser.set_defaults(**{default: config.get(section, key)})

    def set_bool(default, section, key):
        if config.has_option(section, key):
            parser.set_defaults(**{default: config.getboolean(section, key)})

    set_str('pattern_id', 'csv', 'pattern.id')
    set_str('pattern_username', 'csv', 'pattern.username')
    set_str('pattern_repo', 'csv', 'pattern.repo')
    set_str('pattern_description', 'csv', 'pattern.description')
    set_bool('lower_id', 'csv', 'lower.id')
    set_bool('remove_accents', 'csv', 'remove.accents')


def write_config(key, value, global_scope=False):
    config_path = os.path.expanduser("~/.ghot") if global_scope else ".ghot"
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_path)

    section, key = key.split(".", 1)

    if not config.has_section(section):
        config.add_section(section)

    config.set(section, key, value)

    with open(config_path, "w") as configfile:
        config.write(configfile)


def show_config(key=None):
    config = load_config()

    if key is None:
        for section in config.sections():
            print(f"[{section}]")
            for key, value in config.items(section):
                print(f"{key} = {value}")
            print()
        return

    else:
        section = ""
        if "." in key:
            section, key = key.split(".", 1)

        if not config.has_option(section, key):
            if section:
                print(f"Config '{section}.{key}' not found.")
            else:
                print(f"Config '{key}' not found.")
            return

        value = config.get(section, key)
        if section:
            print(f"{section}.{key} = {value}")
        else:
            print(f"{key} = {value}")
