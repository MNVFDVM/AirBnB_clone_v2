#!/usr/bin/python3
"""
Deletes out-of-date archives.
Usage:
    fab -f 100-clean_web_static.py do_clean:number=2 -i ssh-key -u ubuntu > /dev/null 2>&1
"""

import os
from fabric.api import env, run, local, lcd, cd

# Define the list of web servers
env.hosts = ['52.87.155.66', '54.89.109.87']

def do_clean(number=0):
    """Delete out-of-date archives.
    
    Args:
        number (int): The number of archives to keep.
        If number is 0 or 1, keeps only the most recent archive.
        If number is 2, keeps the most and second-most recent archives,
        etc.
    """
    # Set the number to keep
    number = 1 if int(number) == 0 else int(number)

    # Clean local archives
    archives = sorted(os.listdir("versions"))
    if len(archives) > number:
        # Remove archives that are not in the latest 'number'
        archives_to_delete = archives[:-number]
        with lcd("versions"):
            for archive in archives_to_delete:
                local(f"rm ./{archive}")
                print(f"Deleted local archive: versions/{archive}")

    # Clean remote archives
    with cd("/data/web_static/releases"):
        archives = run("ls -tr").split()
        # Filter for relevant archives
        archives = [a for a in archives if "web_static_" in a]
        if len(archives) > number:
            # Remove archives that are not in the latest 'number'
            archives_to_delete = archives[:-number]
            for archive in archives_to_delete:
                run(f"rm -rf ./{{archive}}")
                print(f"Deleted remote archive: /data/web_static/releases/{archive}")

# You can run the script using:
# fab -f 100-clean_web_static.py do_clean:number=2 -i ssh-key -u ubuntu
