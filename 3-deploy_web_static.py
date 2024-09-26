#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to the web servers.
"""

from fabric.api import env, local, put, run
from datetime import datetime
from os.path import exists, isdir

# Define the remote hosts to deploy to
env.hosts = ['34.204.60.80', '54.160.72.183']


def do_pack():
    """
    Generates a .tgz archive from the contents of the web_static folder.
    """
    try:
        # Create the versions directory if it does not exist
        if not isdir("versions"):
            local("mkdir -p versions")
        
        # Create a timestamped archive file name
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = "versions/web_static_{}.tgz".format(date)
        
        # Create the archive
        local("tar -cvzf {} web_static".format(file_name))
        
        # Return the file name if successful
        return file_name
    except Exception as e:
        print(f"Error during packaging: {e}")
        return None


def do_deploy(archive_path):
    """
    Distributes the archive to the web servers.
    """
    if not exists(archive_path):
        print(f"Archive path {archive_path} does not exist.")
        return False
    
    try:
        # Extract the file name and the base name (without extension)
        file_name = archive_path.split("/")[-1]
        no_ext = file_name.split(".")[0]
        release_path = f"/data/web_static/releases/{no_ext}/"
        
        # Upload the archive to /tmp/ directory on the server
        put(archive_path, "/tmp/")
        
        # Create the release directory on the remote server
        run(f"mkdir -p {release_path}")
        
        # Uncompress the archive to the release directory
        run(f"tar -xzf /tmp/{file_name} -C {release_path}")
        
        # Remove the uploaded archive from the /tmp/ directory
        run(f"rm /tmp/{file_name}")
        
        # Move the contents of web_static/ to the release directory
        run(f"mv {release_path}web_static/* {release_path}")
        
        # Remove the empty web_static/ directory
        run(f"rm -rf {release_path}web_static")
        
        # Delete the old symbolic link and create a new one
        run("rm -rf /data/web_static/current")
        run(f"ln -s {release_path} /data/web_static/current")
        
        print("New version deployed successfully!")
        return True
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False


def deploy():
    """
    Creates and distributes an archive to the web servers.
    """
    # Pack the web_static folder into an archive
    archive_path = do_pack()
    
    # If packaging fails, return False
    if archive_path is None:
        print("Packaging failed.")
        return False
    
    # Deploy the archive to the servers
    return do_deploy(archive_path)

