#!/usr/bin/python3
"""
Fabric script that distributes an archive to web servers.
"""

from fabric.api import env, put, run
import os

# Define the list of web servers
env.hosts = ['xx-web-01', 'xx-web-02']  # Replace with your actual server IPs

def do_deploy(archive_path):
    """
    Distributes an archive to web servers.

    Args:
        archive_path (str): The path to the archive to be deployed.

    Returns:
        bool: True if all operations are successful, otherwise False.
    """
    # Check if the archive exists
    if not os.path.exists(archive_path):
        return False

    # Extract the filename without extension
    file_name = os.path.basename(archive_path)
    no_ext = file_name.split('.')[0]
    release_path = f"/data/web_static/releases/{no_ext}/"

    try:
        # Upload the archive to the /tmp/ directory of the web server
        put(archive_path, f"/tmp/{file_name}")

        # Create the release directory
        run(f"mkdir -p {release_path}")

        # Uncompress the archive to the release directory
        run(f"tar -xzf /tmp/{file_name} -C {release_path}")

        # Remove the archive from the web server
        run(f"rm /tmp/{file_name}")

        # Move the contents from web_static folder
        run(f"mv {release_path}web_static/* {release_path}")

        # Remove the web_static folder
        run(f"rm -rf {release_path}web_static")

        # Delete the current symbolic link
        run("rm -rf /data/web_static/current")

        # Create a new symbolic link
        run(f"ln -s {release_path} /data/web_static/current")

        print("New version deployed!")
        return True

    except Exception:
        return False
