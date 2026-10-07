#!/usr/bin/env python3
# -------------------------------------------------------------------------- #
# Filename:     create_flame_wiretap_node.py
# Purpose:      Creates a Flame project node using wiretap_create_node.
# Description:  This script executes a bash command to create a new Autodesk
#               Flame project node via the Wiretap API, using a provided
#               XML configuration.

# Author:       phil_man@mac.com
# Copyright:    Copyright (c) 2025
# Disclaimer:   Disclaimer at bottom of script.
# License:      GNU General Public License v3.0 (GPL-3.0).
#               https://www.gnu.org/licenses/gpl-3.0.en.html

# Version:      2026.2.0
# Status:       Production
# Type:         Utility
# Created:      2025-07-01
# Modified:     2025-10-30

# Changelog:    Changelog at bottom of script.
# -------------------------------------------------------------------------- #

import subprocess
import logging

logger = logging.getLogger(__name__)


def create_flame_wiretap_node(flame_projekt_name, projekt_xml_path):
    """
    Create the logik projekt flame project node using wiretap_create_node.
    """

    bash_command = f"""

    umask 0

    /opt/Autodesk/wiretap/tools/current/wiretap_create_node \
    -h 127.0.0.1:IFFFS \
    -n /projects \
    -t PROJECT \
    -d "{flame_projekt_name}" \
    -s XML \
    -f "{projekt_xml_path}"
    """

    logging.info(f"Running the following bash command:\n{bash_command}")

    process = (
        subprocess.Popen(
            bash_command,
            shell=True,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    )
    stdout, stderr = process.communicate()

    if stdout:
        logging.info(
            f"Command stdout:\n{stdout.decode()}"
        )
    if stderr:
        logging.error(
            f"Command stderr:\n{stderr.decode()}"
        )

    # bjoin studio: a failed register used to be logged and ignored, so the
    # creator built setups/ and launched Flame into a project that did not
    # exist (LC-26_679, 2026-10-07). Stop here instead.
    if process.returncode != 0:
        detail = (stderr or stdout or b"").decode().strip()
        raise RuntimeError(
            f"Flame did not register the project '{flame_projekt_name}'.\n\n"
            f"wiretap_create_node: {detail or 'exit code ' + str(process.returncode)}\n\n"
            f"{WIRETAP_DOWN_HINT}"
        )


WIRETAP_DOWN_HINT = (
    "'No route to host' means Flame's Wiretap (IFFFS) server is not serving "
    "on this station. Restart it, then create the projekt again:\n"
    "  macOS: sudo launchctl kickstart -k system/com.autodesk.sw_ifffs\n"
    "  Linux: sudo systemctl restart adsk_ifffs_wiretap_server\n"
    "'is not empty' means a previous attempt left the Flame project folder "
    "behind: move it aside first."
)


def check_wiretap_projects_reachable():
    """
    bjoin studio preflight: raise unless the local IFFFS Wiretap server
    answers /projects. Runs before anything is written to disk.
    """
    process = subprocess.run(
        [
            "/opt/Autodesk/wiretap/tools/current/wiretap_get_children",
            "-h", "127.0.0.1:IFFFS",
            "-n", "/projects",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        detail = (process.stderr or process.stdout or b"").decode().strip()
        raise RuntimeError(
            "Flame's project service is not answering on this station, so a "
            "new project cannot be registered. Nothing has been created.\n\n"
            f"wiretap_get_children: {detail or 'exit code ' + str(process.returncode)}\n\n"
            f"{WIRETAP_DOWN_HINT}"
        )


# -------------------------------------------------------------------------- #

# DISCLAIMER:   This file is part of LOGIK-PROJEKT.

#               Copyright © 2025 STRENGTH IN NUMBERS

#               LOGIK-PROJEKT creates directories, files, scripts & tools
#               for use with Autodesk Flame and other software.

#               LOGIK-PROJEKT is free software.

#               You can redistribute it and/or modify it under the terms
#               of the GNU General Public License as published by the
#               Free Software Foundation, either version 3 of the License,
#               or any later version.

#               This program is distributed in the hope that it will be
#               useful, but WITHOUT ANY WARRANTY; without even the
#               implied warranty of MERCHANTABILITY or
#               FITNESS FOR A PARTICULAR PURPOSE.

#               See the GNU General Public License for more details.
#               You should have received a copy of the GNU General
#               Public License along with this program.

#               If not, see <https://www.gnu.org/licenses/gpl-3.0.en.html>.

#               Contact: phil_man@mac.com

# -------------------------------------------------------------------------- #
# C2 A9 32 30 32 35 53 54 52 45 4E 47 54 48 2D 49 4E 2D 4E 55 4D 42 45 52 53 #
# -------------------------------------------------------------------------- #
# Changelog:
# -------------------------------------------------------------------------- #
# Version:      2026.2.0
# Modified:     2025-10-30
# Changelist:   Updated version to 2026.2.0.
#               Verified compatibility with Autodesk Flame 2026.2.0.
#               No code changes required.
# -------------------------------------------------------------------------- #
