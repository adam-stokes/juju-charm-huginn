from charms.reactive import (
    hook,
    when,
    only_once,
    is_state
)

import os.path as path
from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from shell import shell

# ./lib/nginxlib
import nginxlib

# ./lib/rubylib
from rubylib import ruby_dist_dir, bundle

# ./lib/dokuwikilib.py
import huginnlib

config = hookenv.config()


# HOOKS -----------------------------------------------------------------------
@hook('config-changed')
def config_changed():

    if not is_state('nginx.available'):
        return

    host.service_restart('nginx')
    hookenv.status_set('active', 'Ready')


# REACTORS --------------------------------------------------------------------
@when('nginx.available')
@only_once
def install_app():
    """ Performs application installation
    """

    hookenv.log('Installing Huginn', 'info')

    # Configure NGINX vhost
    nginxlib.configure_site('default', 'vhost.conf')

    # Update application
    huginnlib.download_archive()
    shell("mkdir -p {}/{log,tmp/pids,tmp/sockets}".format(ruby_dist_dir()))
    shell("cp {}/config/unicorn.rb.example "
          "{}/config/unicorn.rb".format(ruby_dist_dir()))

    bundle("install --deployment --without development test")
    host.service_restart('nginx')
    hookenv.status_set('active', 'Huginn is installed!')


@when('nginx.available', 'database.available')
def setup_mysql(mysql):
    """ Mysql is available, update Huginn
    """
    hookenv.status_set('maintenance', 'Huginn is connecting to MySQL!')
    target = path.join(ruby_dist_dir(), '.env')
    render(source='db.env',
           target=target,
           context=dict(db=mysql))

    bundle("exec rake db:create RAILS_ENV=production")
    bundle("exec rake db:migrate RAILS_ENV=production")
    bundle("exec rake db:seed RAILS_ENV=production")
    bundle("exec rake assets:precompile RAILS_ENV=production")
    host.service_restart('nginx')
    hookenv.status_set('active', 'Ready')
