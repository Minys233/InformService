import yaml
import getpass
from pathlib import Path

from InformService.utils import make_logger

logger = make_logger(__name__)

CACHE_PATH = Path.home() / '.cache/YIS'


def create_credential(name = None):
    if name is None:
        name = input("Template Name: ").strip()
    host = input("Email Server Host: ").strip()
    address = input("Email Address: ").strip()
    passwd = getpass.getpass()
    record = {"Host": host, "Address": address, "Password": passwd}
    with open(CACHE_PATH / (name + '.yaml'), 'w') as fout:
        yaml.dump(record, fout)
    return record


def load_credential(template_name):
    if not CACHE_PATH.is_dir():
        logger.info("Cache dir does not exist, create it.")
    CACHE_PATH.mkdir(parents=True, exist_ok=True)
    templates = list(CACHE_PATH.glob("*.yaml"))
    # if no record template
    if len(templates) == 0:
        logger.info("No template exist, create one")
        return create_credential(template_name)
    # if have templates but template_name not found
    elif CACHE_PATH / (template_name+'.yaml') not in templates:
        return None
    # found
    logger.info(f"Found {template_name}, loading...")
    try:
        saved_record = yaml.load(open(CACHE_PATH / (template_name+'.yaml'), 'r'))
    except FileNotFoundError:
        saved_record = yaml.load(open(CACHE_PATH / (template_name), 'r'))
    return saved_record


def list_credential():
    for name in CACHE_PATH.glob("*.yaml"):
        print(name.name)


