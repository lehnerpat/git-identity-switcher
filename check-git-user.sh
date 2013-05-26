#!/bin/bash

#
#   check-git-user -- check the current committer id for use in bash prompt
#     intended for use in conjunction with:
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

# Note that this script should not be directly executed, but instead sourced
# from your .bashrc or .bash_profile in order to provide the below function for
# use in your bash prompt (PS1).

__check_git_user() {
    USER=$(git config --get user.name)
    EMAIL=$(git config --get user.email)

    if [ -z "$USER" ] && [ -z "$EMAIL" ] ; then
        echo "--"
    else
        ID_USER=$(git config --get-regexp '^id-switcher\.id\.' "$USER")
        ID_EMAIL=$(git config --get-regexp '^id-switcher\.id\.' "$EMAIL")

        if [ -z "$ID_USER" ] || [ -z "$ID_EMAIL" ] ; then #no known ID
            echo "??" # for now -- might use something else at some point
        else
            echo "$(sed 's/^id-switcher\.id\.\(\w\+\)\.name.*/\1/' <<< "$ID_USER")"
        fi
    fi
}

