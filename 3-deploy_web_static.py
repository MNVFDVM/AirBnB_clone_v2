#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to web servers.
"""

from fabric.api import env, local, put, run
import os
from datetime import datetime

# Define the list of web servers
env.hosts = ['xx-web-01', 'xx-web-02']  # Replace with your actual server IPs

def do_pack():
    """
    Creates a .tgz archive from the web_static folder.

    Returns:
        str: The path of the created archive, or None if failed.
    """
    try:
        if not os.path.exists("versions"):
            os.makedirs("versions")

        # Create the archive with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_name = f"versions/web_static_{timestamp}.tgz"
        local(f"tar -cvzf {archive_name} web_static")
        print(f"Packed web_static to {archive_name}")
        return archive_name

    except Exception as e:
        print(f"Error while packing: {e}")
        return None

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

    except Exception as e:
        print(f"Error during deployment: {e}")
        return False

def deploy():
    """
    Creates and distributes an archive to web servers.

    Returns:
        bool: The return value of do_deploy.
    """
    archive_path = do_pack()
    if not archive_path:
        return False

    return do_deploy(archive_path)
