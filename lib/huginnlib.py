from os import path, chdir, makedirs
from charmhelpers.core import hookenv
from shell import shell

from rubylib import ruby_dist_dir, git


def download_archive():
    """
    Downloads Huginn
    """
    hookenv.log("Cloning Huginn", "info")
    dist_dir = ruby_dist_dir()
    if not path.isdir(dist_dir):
        parent_dir = path.dirname(dist_dir)
        if not path.isdir(parent_dir):
            makedirs(parent_dir)
        git("clone --depth 1 https://github.com/cantino/huginn.git "
            "-b master {}".format(dist_dir))
    else:
        chdir(dist_dir)
        git("pull")


def start():
    shell('service php5-fpm start')


def stop():
    shell('service php5-fpm stop')


def restart():
    shell('service php5-fpm restart')
