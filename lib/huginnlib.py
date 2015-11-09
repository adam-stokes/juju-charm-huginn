from os import path, chdir, makedirs
from charmhelpers.core import hookenv
from shell import shell

from rubylib import ruby_dist_dir, git


def download_archive():
    """
    Downloads Huginn
    """
    hookenv.log("Cloning Huginn", "info")
    if not path.isdir(ruby_dist_dir()):
        makedirs(path.dirname(ruby_dist_dir()))
        git("clone --depth 1 https://github.com/cantino/huginn.git "
            "-b master {}".format(ruby_dist_dir()))
    else:
        chdir(ruby_dist_dir())
        git("pull")


def start():
    shell('service php5-fpm start')


def stop():
    shell('service php5-fpm stop')


def restart():
    shell('service php5-fpm restart')
