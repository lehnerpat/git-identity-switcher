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

#### USAGE/HELP PRINTING FUNCTIONS ############################################

HELP_HEADER = "\n    git-indentity-switcher -- quickly switch between Git committer identities"
HELP_FOOTER = """For more details on the meaning of the --global/--local flags, refer to the same
flags in `man git-config`.
"""

def show_help():
    print """{0}
Usage: git-identity-switcher {{--help | -h | <subcommand>}}

Where --help or -h will print this error message and quit.

<subcommand> can be any of:
    add     Add a new ID to the list
    list    Show a list of all existing IDs
    set     Set the active ID to an existing or anonymous one
    show    Show which ID is currently active
    rm      Delete an existing ID from the list
    unset   Unset the current ID
    update  Update the name and email of an existing ID

To get help and usage information on these subcommands, use:

    git-identity-switcher <subcommand> {{--help | -h}}
""".format(HELP_HEADER)

def show_set_usage(showHeader = True, showFooter = True):
    if showHeader:
        print HELP_HEADER
    print """
Usage: git-identity-switcher set [--global | --local] {{<ID> | <name> <email>}}

The option have the following meaning:
    --global    set this ID globally (for all repos)
    --local     set this ID locally (for this repo only)
    <ID>        use the ID known by the given <ID> in the list
    <name>      use an anonymous ID with the given user name
    <email>     use an anonymous ID with the given user email
"""
    if showFooter:
        print HELP_FOOTER


#### ARGUMENT PARSING FUNCTIONS ###############################################

def parse_args():
    i = 1
    # handle globally applicable arguments
    while i < argc and argv[i].startswith("-"):
        if argv[i] == "-h" or argv[i].lower() == "--help": # help message was requested
            show_help() # show help message
            exit(0) # and quit
        else:
            print "Error: Unknown option '{0}'. Ignoring.".format(argv[i])
        i += 1

    if i < argc: # if there are any arguments left
        if argv[i] == "add":
            parse_args_add(i+1)
        elif argv[i] == "list":
            parse_args_list(i+1)
        elif argv[i] == "set":
            parse_args_set(i+1)
        elif argv[i] == "show":
            parse_args_show(i+1)
        elif argv[i] == "rm":
            parse_args_rm(i+1)
        elif argv[i] == "unset":
            parse_args_unset(i+1)
        elif argv[i] == "update":
            parse_args_update(i+1)
        else:
            print "Error: Unknown subcommand '{0}'".format(argv[i])
            show_help()
            exit(2) # TODO: proper exit code
            
    else: # no subcommand was provided, show usage message and quit
        show_help()
        exit(2) # TODO: proper exit code


def parse_args_set(idx):
    if idx >= argc: # if no actual arguments are left
        print "Error: Too few arguments (expected at least one)"
        show_set_usage()
        exit(2) # TODO: proper exit code

    set_location="global"

    set_name = ""
    set_name_set = False
    set_email = ""
    set_email_set = False

    while idx < argc:
        if argv[idx] == "-h" or argv[idx].lower() == "--help":
            show_set_usage()
            exit(0)
        elif argv[idx].lower() == "--local":
            set_location = "local"
        elif argv[idx].lower() == "--global":
            set_location = "global"
        elif not argv[idx].startswith("-"):
            if not set_name_set:
                set_name = argv[idx]
                set_name_set = True
            elif not set_email_set:
                set_email = argv[idx]
                set_email_set = True
            else:
                print "Error: superfluous positional argument '{0}'; ignoring.".format(argv[idx])
        else:
            print "Error: unknown option '{0}'; ignoring.".format(argv[idx])
        idx += 1

    if not set_name_set:
        print "Error: no name or initials were given but are required! Aborting."
        exit(1) # TODO: proper exit code

    if not set_email_set: # we only got a name, assume it's an initial/alias
        ids = get_id_list("global")
        ids.update(get_id_list("local"))
        if set_name in ids:
            set_email = ids[set_name][1]
            set_name = ids[set_name][0]
        else:
            print "Error: no identitiy with the initials '{0}' is known. Aborting.".format(set_name)
            exit(1) # TODO: proper exit code

    id_set(set_name, set_email, set_location)


def parse_args_unset(idx):
    unset_location = "global"
    
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
    add_location = "global"
    add_force = False
    add_id = ''
    add_id_set = False
    add_name = ''
    add_name_set = False
    add_email = ''
    add_email_set = False

    while idx < argc:
        if argv[idx].lower() == "--local":
            add_location = "local"
        elif argv[idx].lower() == "--global":
            add_location = "global"
        elif argv[idx].lower() == "--force" or argv[idx] == "-f":
            add_force = True
        elif argv[idx].lower() == "--no-force":
            add_force = False
        # these inputs are positional and must come last! (in the proper order!)
        elif not argv[idx].startswith('-'):
            if not add_id_set:
                add_id = argv[idx]
                add_id_set = True
            elif not add_name_set:
                add_name = argv[idx]
                add_name_set = True
            elif not add_email_set:
                add_email = argv[idx]
                add_email_set = True
            else:
                print "Error: superfluous positional argument '{0}'; ignoring.".format(argv[idx])
        else:
            print "Error: unknown option '{0}'; ignoring.".format(argv[idx])
        idx += 1

    if len(add_name) == 0 or len(add_email) == 0:
        print "Error: 'name' or 'email' input is empty or missing. Aborting."
        exit(1) # TODO: proper exit code

    id_add_or_update(add_location, add_id, add_name, add_email, add_force, False)


def parse_args_list(idx):
    list_location = "all"

    while idx < argc:
        if argv[idx].lower() == "--local":
            list_location = "local"
        elif argv[idx].lower() == "--global":
            list_location = "global"
        elif argv[idx].lower() == "--all":
            list_location = "all"
        idx += 1

    id_list(list_location)


def parse_args_rm(idx):
    remove_location = "local"
    remove_id = ""
    remove_id_set = False
    
    while idx < argc:
        if argv[idx].lower() == "--local":
            remove_location = "local"
        elif argv[idx].lower() == "--global":
            remove_location = "global"
        #elif argv[idx].lower() == "--local-global":
        #    remove_location = "local-global"
        elif not argv[idx].startswith("-"):
            if not remove_id_set:
                remove_id = argv[idx]
                remove_id_set = True
            else:
                print "Error: superfluous positional argument '{0}'; ignoring.".format(argv[idx])
        else:
            print "Error: unknown option '{0}'; ignoring.".format(argv[idx])
        idx += 1

    if len(remove_id) == 0:
        print "Error: ID initials parameter empty or missing. Aborting."
        exit(1) # TODO: proper exit code

    id_rm(remove_location, remove_id)

def parse_args_update(idx):
    update_location = "global"
    update_id = ''
    update_id_set = False
    update_name = ''
    update_name_set = False
    update_email = ''
    update_email_set = False

    while idx < argc:
        if argv[idx].lower() == "--local":
            update_location = "local"
        elif argv[idx].lower() == "--global":
            update_location = "global"
        # these inputs are positional and must come last! (in the proper order!)
        elif not argv[idx].startswith('-'):
            if not update_id_set:
                update_id = argv[idx]
                update_id_set = True
            elif not update_name_set:
                update_name = argv[idx]
                update_name_set = True
            elif not update_email_set:
                update_email = argv[idx]
                update_email_set = True
            else:
                print "Error: superfluous positional argument '{0}'; ignoring.".format(argv[idx])
        else:
            print "Error: unknown option '{0}'; ignoring.".format(argv[idx])
        idx += 1

    if len(update_name) == 0 or len(update_email) == 0:
        print "Error: 'name' or 'email' input is empty or missing. Aborting."
        exit(1) # TODO: proper exit code

    id_add_or_update(update_location, update_id, update_name, update_email, force=True, update=True)


#### MAIN PROGRAM FUNCTIONS (SUBCOMMANDS) #####################################

def id_set(name, email, location):
    call(['git', 'config', '--' + location, 'user.name', name])
    call(['git', 'config', '--' + location, 'user.email', email])


def id_unset(location):
    call(['git', 'config', '--' + location, '--unset', 'user.name'])
    call(['git', 'config', '--' + location, '--unset', 'user.email'])


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
        if len(user_name) == 0 and len(user_email) == 0:
            print 'Current {0} identity is not set'.format(location)
        else:
            print 'Current {0} identity: "{1} <{2}>"'.format(location, user_name, user_email)

def id_add_or_update(location, new_id, name, email, force, update):
    name_key = 'id-switcher.id.' + new_id + '.name'
    email_key = 'id-switcher.id.' + new_id + '.email'

    proc = Popen(['git', 'config', '--null', '--' + location, '--get', name_key], stdout=PIPE)
    pipe = proc.stdout
    proc.wait()
    user_name = pipe.read()
    pipe.close()
    namereturncode = proc.returncode

    proc = Popen(['git', 'config', '--null', '--' + location, '--get', email_key], stdout=PIPE)
    pipe = proc.stdout
    proc.wait()
    user_email = pipe.read()
    pipe.close()
    emailreturncode = proc.returncode

    if namereturncode == 2 or emailreturncode == 2:
        if namereturncode == 2:  print "git-config reports that multiple values exist for " + location + " key " + name_key
        if emailreturncode == 2: print "git-config reports that multiple values exist for " + location + " key " + email_key
        print "This is incompatible with git-identitiy-switcher. Please fix it manually."
        if not update:
            print "\nNew ID '{0}' could not be added.".format(new_id)
        else:
            print "\nID '{0}' could not be updated.".format(new_id)
        exit(1) # TODO: proper exit code

    if update:
        if namereturncode == 1 or emailreturncode == 1:
            if namereturncode == 1:  print location + " config key " + name_key + " does not exist."
            if emailreturncode == 1: print location + " config key " + email_key + " does not exist."
            print "If you want to create this ID, please use the 'add' subcommand."
            print "\nID '{0}' could not be updated.".format(new_id)
            exit(1) # TODO: proper exit code
    elif (namereturncode == 0 or emailreturncode == 0) and not force:
        if namereturncode == 0:  print location + " config key " + name_key + " already exists."
        if emailreturncode == 0: print location + " config key " + email_key + " already exists."
        print "If you want to overwrite this ID, please append the --force switch."
        print "\nNew ID '{0}' could not be added.".format(new_id)
        exit(1) # TODO: proper exit code

    call(['git', 'config', '--' + location, name_key, name])
    call(['git', 'config', '--' + location, email_key, email])

def id_list(location):
    if location == "global" or location == "all":
        id_list_section('global')

    if location == "local" or location == "all":
        id_list_section('local')

def id_list_section(location):
    ids = get_id_list(location)
    for key, value in ids.iteritems():
        print '[{0}] "{1}": "{2} <{3}>"'.format(location, key, value[0], value[1])

def id_rm(location, remove_id):
    name_key = 'id-switcher.id.' + remove_id + '.name'
    email_key = 'id-switcher.id.' + remove_id + '.email'

    proc = Popen(['git', 'config', '--null', '--' + location, '--get', name_key], stdout=PIPE)
    pipe = proc.stdout
    proc.wait()
    user_name = pipe.read()
    pipe.close()
    namereturncode = proc.returncode

    proc = Popen(['git', 'config', '--null', '--' + location, '--get', email_key], stdout=PIPE)
    pipe = proc.stdout
    proc.wait()
    user_email = pipe.read()
    pipe.close()
    emailreturncode = proc.returncode

    if namereturncode == 2 or emailreturncode == 2:
        if namereturncode == 2:  print "git-config reports that multiple values exist for " + location + " key " + name_key
        if emailreturncode == 2: print "git-config reports that multiple values exist for " + location + " key " + email_key
        print "This is incompatible with git-identitiy-switcher. Please fix it manually."
        print "\nID '{0}' could not be removed.".format(remove_id)
        exit(1) # TODO: proper exit code

    if namereturncode == 1 and emailreturncode == 1:
        print "Error: {1} ID '{0}' does not exist.".format(remove_id, location)
        exit(1) # TODO: proper exit code

    if namereturncode == 1: 
        print "Warning: {0} config key {1} does not exist.".format(location, name_key)
    else:
        call(['git', 'config', '--unset', '--' + location, name_key])

    if emailreturncode == 1:
        print "Warning: {0} config key {1} does not exist.".format(location, email_key)
    else:
        call(['git', 'config', '--unset', '--' + location, email_key])


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

def get_id_list(location):
    pipe = Popen(['git', 'config', '--' + location, '--get-regexp', '^id-switcher\.id\.'], stdout=PIPE).stdout
    vallist = pipe.read()
    pipe.close()

    ids = {}

    for val in vallist.splitlines():
        parts = val.split(' ', 1)
        keyparts = parts[0].split('.')
        key = keyparts[2]
        keytype = keyparts[3]
        if not key in ids:
            ids[key] = ['', '']
        if keytype == "name":
            ids[key][0] = parts[1]
        elif keytype == "email":
            ids[key][1] = parts[1]

    return ids
        
        
    


#### MAIN PROGRAM PART ########################################################

argc = len(argv)
parse_args()

