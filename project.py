import os
from libs.format_bytes import format_bytes
from libs.format_date import pretty_date
import hashlib
from libs.db import insert_project, get_project_by_id, update_project, update_project_property, delete_project_by_id
import platform
import shutil
import config_parser as cfg

config = cfg.read_config()
NAMESPACE = config['namespace']
PROMAN_DATA_DIR = config['data_dir']


class Project:
    def __init__(self, name, namespace,  project_meta=None):
        self.name = name
        self.namespace = namespace if not project_meta else project_meta['namespace']
        self.uid = self.get_uid()
        self.project_meta = project_meta
        self.is_active = self.project_meta['is_active'] if project_meta else True
        self.full_path = os.path.join(
            PROMAN_DATA_DIR, self.namespace, 'active', self.name)
        self.archive_full_path = os.path.join(
            PROMAN_DATA_DIR, self.namespace, 'archived', self.name)

        if(self.is_active):
            self.last_mod = self.get_last_mod_time()
            self.created_time = self.get_created_time()
            self.size = self.get_size()
            self.compressed_size = self.project_meta['compressed_size'] if project_meta else None

        else:
            self.last_mod = self.project_meta['last_mod']
            self.created_time = self.project_meta['created_time']
            self.size = self.project_meta['size']
            self.compressed_size = self.project_meta['compressed_size']

    def get_pretty_size(self, size=None):
        if size == None:
            size = self.size
        return(format_bytes(size))

    def get_last_mod_time(self):
        return(os.path.getmtime(self.full_path))

    def get_created_time(self):
        if platform.system() == 'Windows':
            return os.path.getctime(self.full_path)
        else:
            stat = os.stat(self.full_path)
            try:
                return stat.st_birthtime
            except AttributeError:
                return stat.st_ctime

    def get_pretty_last_mod(self):
        return(pretty_date(self.last_mod))

    def get_pretty_created_time(self):
        return(pretty_date(self.created_time))

    def get_uid(self):
        h = hashlib.new('sha1')
        h.update(self.name.encode("utf-8"))
        h.update(self.namespace.encode("utf-8"))
        return h.hexdigest()

    def get_uid_short(self):
        return self.uid[0:6]

    def get_size(self):
        project = get_project_by_id(self.uid)
        if self.project_meta and self.project_meta["last_mod"] == self.last_mod:
            return self.project_meta["size"]
        else:
            size = self.calc_dir_size()
            if project:
                update_project_property(
                    {'size': size, 'last_mod': self.last_mod}, self.uid)
            return size

    def calc_dir_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.full_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    def compress(self):
        archive = shutil.make_archive(
            self.archive_full_path, 'zip', self.full_path)
        size = os.path.getsize(archive)
        self.compressed_size = size
        update_project_property(
            {'is_active': False, 'compressed_size': size}, self.uid)
        return 0

    def decompress(self):
        shutil.unpack_archive(self.archive_full_path +
                              '.zip', self.full_path, 'zip')
        update_project_property({'is_active': True}, self.uid)
        return 0

    def delete_active(self):
        shutil.rmtree(self.full_path)
        return 0

    def delete_archive(self):
        os.remove(self.archive_full_path+'.zip')
        return 0

    def delete_project(self):
        if self.is_active:
            self.delete_active()
        else:
            self.delete_archive()
        delete_project_by_id(self.uid)

    def save(self):
        itm = {
            "uid": self.uid,
            "short_uid": self.get_uid_short(),
            "name": self.name,
            "namespace": self.namespace,
            "size": 0,
            "last_mod": self.last_mod,
            "created_time": self.created_time,
            "full_path": self.full_path,
            "is_active": True,
            "archive_full_path": self.archive_full_path,
            "compressed_size": None
        }
        insert_project(itm)
