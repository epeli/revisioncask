# -*- coding: utf-8 -*-
"""
Copyright (C) 2010 Esa-Matti Suuronen <esa-matti@suuronen.org>

This file is part of subssh.

Subssh is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

Subssh is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with Subssh.  If not, see
<http://www.gnu.org/licenses/>.
"""

import os
from ConfigParser import SafeConfigParser

import subssh
from abstractrepo import VCS
from abstractrepo import vcs_init
from repomanager import RepoManager


class config:
    SVNSERVE_BIN = "svnserve"

    SVN_BIN = "svn"

    SVNADMIN_BIN = "svnadmin"

    REPOSITORIES = os.path.join(subssh.config.SUBSSH_HOME, "vcs", "svn", "repos")
    HOOKS_DIR = os.path.join(subssh.config.SUBSSH_HOME, "vcs", "svn", "hooks")

    WEB_DIR = os.path.join( os.environ["HOME"], "repos", "websvn" )

    URL_RW =  "svn+ssh://$hostusername@$hostname/$name_on_fs"
    URL_WEB_VIEW =  "http://$hostname/websvn/listing.php?repname=$name_on_fs"




    MANAGER_TOOLS = "true"

class Subversion(VCS):
    required_by_valid_repo = ("conf/svnserve.conf",)
    permdb_name= "conf/" + VCS.permdb_name
    # For svnserve, "/" stands for whole repository
    _permissions_section = "/"

    def _create_repository_files(self):

        path = self.repo_path

        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.abspath(path)

        subssh.check_call((config.SVNADMIN_BIN, "create", path))
        subssh.check_call((
                          config.SVN_BIN, "-m", "automatically created project base",
                          "mkdir", "file://%s" % os.path.join(path, "trunk"),
                                   "file://%s" % os.path.join(path, "tags"),
                                   "file://%s" % os.path.join(path, "branches"),
                          ))



    def _enable_svn_perm(self):
        """
        Set Subversion repository to use our permission config file
        """
        confpath = os.path.join(self.repo_path, "conf/svnserve.conf")
        conf = SafeConfigParser()
        conf.read(confpath)
        conf.set("general", "authz-db", self.permdb_name)
        f = open(confpath, "w")
        conf.write(f)
        f.close()


class SubversionManager(RepoManager):

    klass = Subversion







    def activate_hooks(self, user, repo_name):
        """TODO"""

    def copy_common_hooks(self, user, repo_name):
        ""
        # TODO: implement



@subssh.no_interactive
@subssh.expose_as("svnserve")
def handle_svn(user, *args):

    # Subversion can handle itself permissions and virtual root.
    # So there's no need to manually check permissions here or
    # transform the virtual root.
    return subssh.call((config.SVNSERVE_BIN,
                            '--tunnel-user=' + user.username,
                            '-t', '-r',
                            repos_path_with_svn_prefix))







def appinit():

    vcs_init(config)

    if subssh.to_bool(config.MANAGER_TOOLS):
        manager = SubversionManager(config.REPOSITORIES,
                                    web_repos_path=config.WEB_DIR,
                                    urls={'rw': config.URL_RW,
                                          'webview': config.URL_WEB_VIEW},
                                     )

        subssh.expose_instance(manager, prefix="svn-")

