#!/usr/bin/python3
# Fabric script that generates a .tgz archive from the
# contents of the web_static folder of your AirBnB Clone repo
# using the function do_deploy

import os
from fabric.api import run, put, env

env.hosts = ['34.204.60.80', '54.160.72.183']
env.user = "ubuntu"

def do_deploy(archive_path):
    """Distribute an archive to web servers."""
    if not os.path.exists(archive_path):
        return False

    try:
        # Upload the archive to the /tmp/ directory on the server
        put(archive_path, "/tmp/")
        
        # Extract the archive file name (without the path)
        file_name = os.path.basename(archive_path)
        
        # Extract the base name (without extension)
        file_name_no_ext = file_name.split(".")[0]
        
        # Set up the final release folder path
        final_dir = f"/data/web_static/releases/{file_name_no_ext}/"
        
        # Create the directory where the archive will be unpacked
        run(f"mkdir -p {final_dir}")
        
        # Unpack the archive in the newly created directory
        run(f"tar -xzf /tmp/{file_name} -C {final_dir}")
        
        # Remove the archive from the /tmp/ directory
        run(f"rm /tmp/{file_name}")
        
        # Move the contents out of the web_static directory to the final release directory
        run(f"mv {final_dir}web_static/* {final_dir}")
        
        # Remove the now-empty web_static directory
        run(f"rm -rf {final_dir}web_static")
        
        # Remove the old symbolic link, if it exists
        run("rm -rf /data/web_static/current")
        
        # Create a new symbolic link to the new version
        run(f"ln -s {final_dir} /data/web_static/current")
        
        print("New version deployed successfully!")
        return True

    except Exception as e:
        print(f"Deployment failed: {e}")
        return False
