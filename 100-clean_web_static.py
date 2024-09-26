#!/usr/bin/python3
"""
Fabric script that deletes out-of-date archives.
"""

from fabric.api import env, run, local
import os

# Define the list of web servers
env.hosts = ['xx-web-01', 'xx-web-02']  # Replace with your actual server IPs

def do_clean(number=0):
    """
    Deletes out-of-date archives from local and remote servers.

    Args:
        number (int): The number of archives to keep.
    """
    # Clean local archives
    local_archives = sorted(os.listdir("versions"))
    if number == 0 or number == 1:
        number_to_keep = 1
    else:
        number_to_keep = number

    # Get the archives to delete
    archives_to_delete = local_archives[:-number_to_keep]
    for archive in archives_to_delete:
        local(f"rm versions/{archive}")
        print(f"Deleted local archive: versions/{archive}")

    # Clean remote archives
    for host in env.hosts:
        run(f"cd /data/web_static/releases && ls -t | tail -n +{number_to_keep + 1} | xargs -I{{}} rm -rf {{}}")
        print(f"Deleted outdated remote archives on {host}")

# You can run the script using:
# fab -f 100-clean_web_static.py do_clean:number=2 -i my_ssh_private_key -u ubuntu
