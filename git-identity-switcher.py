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

DEFAULT_LOCATION = "global"

def show_help():
    print """
    git-indentity-switcher -- quickly switch between Git committer identities
    """

def show_set_usage():
    pass

def id_set(name,email="",location=DEFAULT_LOCATION):
    print "Name=", name
    print "Email=", email
    print "loc=", location

def id_show(args):
    pass

def id_add(args):
    pass

def id_list(args):
    pass

def id_rm(args):
    pass

def id_update(args):
    pass

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


def parse_args_add(idx):
    pass

argc = len(argv)
parse_args()

print "done"
