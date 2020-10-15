import os
import sys
import shutil
import argparse
import display as dp
import libs.cp as cp
import config_parser as cfg
import libs.termcolors as tc
from tabulate import tabulate
from libs.y_n_prompt import yn
from libs.string_validators import check_hex

if cfg.if_cfg_file_exists():
    from project import Project
    import libs.db as db

parser = argparse.ArgumentParser(description='Project manager v0.0.1')
parser.add_argument(
    "--init", help="Initialize proman, setup directories and db", action="store_true")
parser.add_argument(
    "-c", "--create-project", help="Create new empty project", action="store")
parser.add_argument(
    "--create-namespace", help="Create new namespace", action="store")
parser.add_argument(
    "-a", "--activate", help="Activate project", action="store")
parser.add_argument(
    "-x", "--archive", help="Archive project", action="store")
parser.add_argument(
    "-r", "--delete", help="Permanently delete a project", action="store")
parser.add_argument(
    "-d", "--describe", help="Detailed description of project", action="store")
parser.add_argument(
    "-n", "--namespace", help="Specify namespace", action="store")
parser.add_argument(
    "-g", "--list-global", help="List all projects(all namespaces)", action="store_true")
parser.add_argument(
    "-l", "--list-active", help="List active projects", action="store_true")
parser.add_argument(
    "-z", "--list-archived", help="List archived projects", action="store_true")
parser.add_argument(
    "--migrate", help="Migrate existing project", action="store")

args = parser.parse_args()

NAMESPACE = None
PROMAN_DATA_DIR = None


def main():
    if(len(sys.argv) < 2):
        no_args()
    if(args.init):
        init_proman()
        return
    else:
        set_config()

    if(args.namespace):
        set_namespace()

    if(args.list_active):
        list_active_projects()
        return
    if(args.list_archived):
        list_archived_projects()
        return
    if(args.list_global):
        list_global()
        return
    if(args.describe):
        describe_project(args.describe)
        return
    if(args.archive):
        archive_project()
        return
    if(args.activate):
        activate_project()
        return
    if(args.create_project):
        create_project()
        return
    if(args.create_namespace):
        create_namespace()
        return
    if(args.delete):
        delete_project()
        return
    if(args.migrate):
        migrate_project()
        return


def set_config():
    global NAMESPACE
    global PROMAN_DATA_DIR

    if not cfg.if_cfg_file_exists():
        print("[-] Configuration File not found, please run proman --init")
        sys.exit(1)

    config = cfg.read_config()
    NAMESPACE = config['namespace']
    PROMAN_DATA_DIR = config['data_dir']

    return 0


def set_namespace():
    global NAMESPACE
    ns = args.namespace
    if os.path.exists(os.path.join(PROMAN_DATA_DIR, ns)):
        NAMESPACE = ns
    else:
        print("[-] Invalid Namespace")
        sys.exit()


def init_proman():
    print("[+] Initializing proman")
    in_dir = input("[*] Please enter a valid directory : ")
    if not os.path.exists(in_dir):
        print("[+] Directory doesnt exist")
        return
    cfg.write_config(in_dir)
    set_config()
    create_namespace('default')
    print("[+] Successfully created all directories, Happy coding!")
    return 0


def no_args():
    print("Proman Version 0.0.1")
    print("use -h / --help for help menu")


def create_namespace(namespace=args.create_namespace):
    namespace_dir = os.path.join(PROMAN_DATA_DIR, namespace)
    if namespace == 'all':
        print("[!] Not a valid namespace")
    if os.path.exists(namespace_dir):
        print("[-] Namespace %s already exists" % (namespace))
        return 1
    os.makedirs(os.path.join(namespace_dir, 'active'))
    os.makedirs(os.path.join(namespace_dir, 'archived'))
    return 0


def describe_project(uid):
    meta = get_project(uid)
    p = Project(meta['name'], NAMESPACE, meta)
    if(p):
        dp.describe(p)


def get_project(p):
    project = []
    if(len(p) == 6 and check_hex(p)):
        project = db.get_project_by_short_id(p)
    elif len(p) == 40 and check_hex(p):
        project = db.get_project_by_id(p)
    else:
        project = db.get_project_by_name(p, NAMESPACE)
    if project and len(project) > 1:
        print("[!] Multiple projects with same short id detected")
        sys.exit(1)

    if len(project) < 1:
        print("[-] No records found with id %s" % (p))
        sys.exit(1)
    else:
        return project[0]


def list_active_projects():
    projects = db.get_all_active_projects_by_namespace(NAMESPACE)
    if len(projects) < 1:
        print("[-] Wow, such empty. No records found in namespace ", NAMESPACE)
        return 0
    active_project_list = []
    for meta in projects:
        active_project_list.append(Project(meta['name'],  NAMESPACE, meta))
    dp.active(active_project_list)


def list_archived_projects():
    projects = db.get_all_archived_projects_by_namespace(NAMESPACE)

    if len(projects) < 1:
        print("[-] Wow, such empty. No records found in namespace ", NAMESPACE)
        return 0
    archive_project_list = []
    for meta in projects:
        archive_project_list.append(Project(meta['name'],  NAMESPACE, meta))
    dp.archive(archive_project_list)


def list_global():
    project_list = []
    for meta in db.get_all_global():
        project_list.append(Project(meta['name'],  NAMESPACE, meta))
    dp.global_list(project_list)


def archive_project():
    meta = get_project(args.archive)
    project = Project(meta['name'], NAMESPACE, meta)
    if not project.is_active:
        print('[-] Project is already archived')
        return 1
    if not os.listdir(project.full_path):
        print('[-] Empty directory. No need to archive')
        return 1
    print('[+] Compressing files')
    project.compress()
    project.delete_active()
    print('[+] Project archived')
    print('[i] {} of space freed!'.format(
        project.get_pretty_size(project.size - project.compressed_size)))


def activate_project():
    meta = get_project(args.activate)
    project = Project(meta['name'], NAMESPACE, meta)
    if project.is_active:
        print('[-] Project is already activated')
        return 1
    print('[+] Decompressing archive')
    project.decompress()
    project.delete_archive()
    print('[+] Project active!')


def delete_project():
    meta = get_project(args.delete)
    project = Project(meta['name'], NAMESPACE, meta)
    print(
        tc.color.RED,
        u'\U0001F5D1',
        tc.color.END,
        '[warning] Delete operation: Files will be permanently deleted! continue ? [y/n]',
        end=" "
    )
    if yn():
        print('[i] Deleting ', project.name)
        project.delete_project()
        print('[+] Done')
    else:
        print('[-] Operation aborted ny user')


def create_project(project_name=args.create_project):
    active_dir = os.path.join(PROMAN_DATA_DIR, NAMESPACE, 'active')
    project_path = os.path.join(active_dir, project_name)
    if os.path.exists(project_path):
        print("[-] Project named %s already exists in namespace %s" %
              (project_name, NAMESPACE))
        return 0
    os.mkdir(project_path)
    print('[+] Creating new project {} in {}'.format(project_name, NAMESPACE))
    project = Project(project_name, NAMESPACE)
    project.save()
    print('[+] Done')
    return project


def migrate_project():
    project_path = os.path.abspath(args.migrate)
    if not os.path.exists(project_path):
        print('[-] Directory doesnt exist')
        return
    project_name = os.path.basename(project_path)
    project_name = project_name.replace(' ', '-').lower().strip()
    project = create_project(project_name)
    if not project:
        return
    print('[+] Copying files')
    cp.from_folder(project_path, project.full_path)
    print('[+] Deleting old files')
    shutil.rmtree(project_path)
    print('[+] Project migrated')


if __name__ == "__main__":
    main()
