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

# ./lib/huginnlib.py
import huginnlib

config = hookenv.config()


# HOOKS -----------------------------------------------------------------------
@hook('config-changed')
def config_changed():

    if not is_state('nginx.available'):
        return

    target = path.join(ruby_dist_dir(), '.env.local')
    render(source='app.env',
           target=target,
           context=config)

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
    nginxlib.configure_site('default', 'vhost.conf',
                            app_path=ruby_dist_dir())

    # Update application
    huginnlib.download_archive()
    shell("mkdir -p %s/{log,tmp/pids,tmp/sockets}" % (ruby_dist_dir()))
    shell("cp %(dir)s/config/unicorn.rb.example "
          "%(dir)s/config/unicorn.rb" % {'dir': ruby_dist_dir()})

    bundle("install --deployment --without development test")
    procfile = path.join(hookenv.charm_dir(), 'templates/Procfile')
    shell("cp %(procfile)s %(dir)s/Procfile" % {
        'procfile': procfile,
        'dir': ruby_dist_dir()
    })

    bundle("exec rake assets:precompile RAILS_ENV=production")

    host.service_restart('nginx')
    hookenv.status_set('active', 'Huginn is installed!')


@when('nginx.available', 'database.available')
def setup_mysql(mysql):
    """ Mysql is available, update Huginn
    """
    hookenv.status_set('maintenance', 'Huginn is connecting to MySQL!')
    target = path.join(ruby_dist_dir(), '.env.local')
    render(source='db.env',
           target=target,
           context=dict(db=mysql))

    bundle("exec rake db:create RAILS_ENV=production")
    bundle("exec rake db:migrate RAILS_ENV=production")
    bundle("exec rake db:seed RAILS_ENV=production")
    host.service_restart('nginx')
    hookenv.status_set('active', 'Ready')
