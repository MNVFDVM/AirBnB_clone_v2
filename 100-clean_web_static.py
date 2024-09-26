#!/usr/bin/python3
"""
do_pack(): Generates a .tgz archive from the
contents of the web_static folder.
do_deploy(): Distributes an archive to a web server.
deploy(): Creates and distributes an archive to a web server.
do_clean(): Deletes out-of-date archives.
"""

from fabric.operations import local, run, put
from datetime import datetime
import os
from fabric.api import env

env.hosts = ['34.204.60.80', '54.160.72.183']


def do_pack():
    """
    Function to compress files in an archive.
    """
    try:
        local("mkdir -p versions")
        filename = "versions/web_static_{}.tgz".format(
            datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        )
        result = local("tar -cvzf {} web_static".format(filename))
        if result.failed:
            return None
        return filename
    except Exception as e:
        print(f"Error during packing: {e}")
        return None


def do_deploy(archive_path):
    """
    Function to distribute an archive to a server.
    """
    if not os.path.exists(archive_path):
        return False

    try:
        # Extract filename without path and extension
        filename = archive_path.split("/")[-1].split(".")[0]

        # Upload the archive to /tmp/ on the server
        res = put(archive_path, f"/tmp/{filename}.tgz")
        if res.failed:
            return False

        # Create the release folder
        res = run(f"mkdir -p /data/web_static/releases/{filename}/")
        if res.failed:
            return False

        # Unpack the archive into the release folder
        res = run(f"tar -xzf /tmp/{filename}.tgz -C /data/web_static/releases/{filename}/")
        if res.failed:
            return False

        # Remove the archive from /tmp/
        res = run(f"rm /tmp/{filename}.tgz")
        if res.failed:
            return False

        # Move the contents to the correct location
        res = run(f"mv /data/web_static/releases/{filename}/web_static/* /data/web_static/releases/{filename}/")
        if res.failed:
            return False

        # Remove the empty web_static directory
        res = run(f"rm -rf /data/web_static/releases/{filename}/web_static")
        if res.failed:
            return False

        # Remove the old symbolic link and create a new one
        res = run("rm -rf /data/web_static/current")
        if res.failed:
            return False

        res = run(f"ln -s /data/web_static/releases/{filename}/ /data/web_static/current")
        if res.failed:
            return False

        print('New version deployed successfully!')
        return True
    except Exception as e:
        print(f"Error during deployment: {e}")
        return False


def deploy():
    """
    Creates and distributes an archive to a web server.
    """
    filepath = do_pack()
    if filepath is None:
        return False
    return do_deploy(filepath)


def do_clean(number=0):
    """
    Deletes out-of-date archives.
    The number argument is the number of most recent archives to keep.
    If number is 0 or 1, it will keep only the most recent archive.
    """
    number = int(number)
    number = 1 if number == 0 else number

    # Clean local archives
    local_archives = local("ls -1t versions", capture=True).split("\n")
    for archive in local_archives[number:]:
        local(f"rm -rf versions/{archive}")

    # Clean remote archives
    remote_archives = run("ls -1t /data/web_static/releases").split("\n")
    for archive in remote_archives[number:]:
        if "test" not in archive:
            run(f"rm -rf /data/web_static/releases/{archive}")
