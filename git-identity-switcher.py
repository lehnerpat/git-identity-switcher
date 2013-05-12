#!/usr/bin/env python

#
#   git-indentity-switcher -- quickly switch between Git committer identities
#
# Copyright (C) 2013  Nevik Rehnel <hai.kataker@gmx.de>
#
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

from sys import argv
from subprocess import *

DEFAULT_LOCATION = "global"

#### USAGE/HELP PRINTING FUNCTIONS ############################################

def show_help():
    print """
    git-indentity-switcher -- quickly switch between Git committer identities
    """

def show_set_usage():
    pass


#### ARGUMENT PARSING FUNCTIONS ###############################################

def parse_args():
    i = 0
    # handle globally applicable arguments
    for i in range(1,argc):
        if not argv[i].startswith("-"):
            i -= 1
            break
        if argv[i] == "-h" or argv[i].lower() == "--help": # help message was requested
            show_help() # show help message
            exit(0) # and quit

    i += 1
    if i < argc: # if there are any arguments left
        if argv[i] == "set":
            parse_args_set(i+1)
        elif argv[i] == "unset":
            parse_args_unset(i+1)
        elif argv[i] == "show":
            parse_args_show(i+1)
        elif argv[i] == "add":
            parse_args_add(i+1)
            
    else: # no subcommand was provided, show usage message and quit
        show_help()
        exit(2)


def parse_args_set(idx):
    if argc - idx < 1: # if no actual arguments are left
        print "ERROR: Too few arguments (expected at least one)"
        show_set_usage()
        exit(2)
    set_name = argv[idx]
    idx += 1
    if idx < argc:
        set_email = argv[idx]
    else:
        set_email = ""
    set_location=DEFAULT_LOCATION
    
    id_set(set_name, set_email, set_location)


def parse_args_unset(idx):
    unset_location = DEFAULT_LOCATION
    
    while idx < argc:
        if argv[idx].lower() == "--local":
            unset_location = "local"
        elif argv[idx].lower() == "--global":
            unset_location = "global"
        idx += 1

    id_unset(unset_location)


def parse_args_show(idx):
    show_location = "all"
    show_empty = False

    while idx < argc:
        if argv[idx].lower() == "--local":
            show_location = "local"
        elif argv[idx].lower() == "--global":
            show_location = "global"
        elif argv[idx].lower() == "--all":
            show_location = "ALL"
        idx += 1

    id_show(show_location)


def parse_args_add(idx):
    pass


#### MAIN PROGRAM FUNCTIONS (SUBCOMMANDS) #####################################

def id_set(name, email, location):
    if location == "local" or location == "global":
        call(['git', 'config', '--' + location, 'user.name', '"' + name + '"'])
        call(['git', 'config', '--' + location, 'user.email', '"' + email + '"'])
    # TODO: add error message if unsupported location


def id_unset(location):
    if location == "local" or location == "global":
        call(['git', 'config', '--' + location, '--unset', 'user.name'])
        call(['git', 'config', '--' + location, '--unset', 'user.email'])
    # TODO: add error message if unsupported location


def id_show(location):
    if location == "ALL":
        location = "all"
        show_empty = True
    else:
        show_empty = False
    if location == "global" or location == "all":
        id_show_one("global", show_empty)
    if location == "local" or location == "all":
        id_show_one("local", show_empty)

def id_show_one(location, show_empty):
    (user_name, user_email) = get_current_id(location)
    if len(user_name) != 0 or len(user_email) != 0 or show_empty:
        if len(user_name) == 0:
            user_name_suffix = " (UNSET)"
        else:
            user_name_suffix = ""
        if len(user_email) == 0:
            user_email_suffix = " (UNSET)"
        else:
            user_email_suffix = ""
        print '[{0}] user.name  = "{1}"{2}'.format(location, user_name, user_name_suffix)
        print '[{0}] user.email = "{1}"{2}'.format(location, user_email, user_email_suffix)

def id_add(args):
    pass

def id_list(args):
    pass

def id_rm(args):
    pass

def id_update(args):
    pass


#### UTILITY AND HELPER FUNCTIONS #############################################

def get_current_id(location):
    pipe = Popen(['git', 'config', '--null', '--' + location, '--get', 'user.name'], stdout=PIPE).stdout
    user_name = pipe.read()
    pipe.close()

    pipe = Popen(['git', 'config', '--null', '--' + location, '--get', 'user.email'], stdout=PIPE).stdout
    user_email = pipe.read()
    pipe.close()

    if len(user_name.strip()) == 0:
        user_name = ""
    if len(user_email.strip()) == 0:
        user_email = ""

    return (user_name, user_email)
    


#### MAIN PROGRAM PART ########################################################

argc = len(argv)
parse_args()

print "done"
