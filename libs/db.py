from tinydb import TinyDB, Query
import config_parser as cfg
import os

config = cfg.read_config()
DB_PATH = os.path.join(config['config_dir'], "project.json")

project = Query()
projects_db = TinyDB(DB_PATH)


def insert_project(item):
    return projects_db.insert(item)


def update_project(item):
    return projects_db.update(item, project.uid == item['id'])


def update_project_property(prop, uid):
    return projects_db.update(prop, project.uid == uid)


def get_project_by_name(name, namespace):
    return projects_db.search((project.name == name) & (project.namespace == namespace))


def get_project_by_id(uid):
    return projects_db.search(project.uid == uid)


def get_project_by_short_id(uid):
    return projects_db.search(project.short_uid == uid)


def get_all_projects_by_namespace(namespace):
    return projects_db.search(project.namespace == namespace)


def get_all_active_projects_by_namespace(namespace):
    return projects_db.search((project.is_active == True) & (project.namespace == namespace))


def get_all_archived_projects_by_namespace(namespace):
    return projects_db.search((project.is_active == False) & (project.namespace == namespace))


def delete_project_by_id(uid):
    return projects_db.remove(project.uid == uid)


def get_all_namespaces():
    return list(set([r['namespace']
                     for r in projects_db.search(project.uid != 1)]))


def get_all_global():
    return projects_db.search(project.uid != 1)
