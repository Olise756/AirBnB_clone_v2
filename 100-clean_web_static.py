#!/usr/bin/python3

"""A module for web application deployment with Fabric."""
import os
from datetime import datetime
from fabric.api import env, local, put, run, runs_once


env.hosts = ["34.73.0.174", "35.196.78.105"]
"""The list of host server IP addresses."""


@runs_once
def do_pack():
    """ This Archives the static files."""
    if not os.path.isdir("versions"):
        os.mkdir("versions")
    cursor_time = datetime.now()
    output = "versions/web_static_{}{}{}{}{}{}.tgz".format(
        cursor_time.year,
        cursor_time.month,
        cursor_time.day,
        cursor_time.hour,
        cursor_time.minute,
        cursor_time.second
    )
    try:
        print("Packing web_static to {}".format(output))
        local("tar -cvzf {} web_static".format(output))
        archize_size = os.stat(output).st_size
        print("web_static packed: {} -> {} Bytes".format(output, archize_size))
    except Exception:
        output = None
    return output


def do_deploy(archivepath):
    """This Deploys the static files to the host servers.
    Args:
        archive_path (str): The path to the archived static files.
    """
    if not os.path.exists(archivepath):
        return False
    filename = os.path.basename(archivepath)
    foldername = filename.replace(".tgz", "")
    folderpath = "/data/web_static/releases/{}/".format(foldername)
    success = False
    try:
        put(archive_path, "/tmp/{}".format(filename))
        run("mkdir -p {}".format(folderpath))
        run("tar -xzf /tmp/{} -C {}".format(filename, folderpath))
        run("rm -rf /tmp/{}".format(file_name))
        run("mv {}web_static/* {}".format(folderpath, folderpath))
        run("rm -rf {}web_static".format(folderpath))
        run("rm -rf /data/web_static/current")
        run("ln -s {} /data/web_static/current".format(folderpath))
        print('New version deployed!')
        success = True
    except Exception:
        success = False
    return success


def deploy():
    """This Archives and deploys the static files to the host servers.
    """
    archivepath = do_pack()
    return do_deploy(archivepath) if archive_path else False


def do_clean(number=0):
    """Deletes out-of-date archives of the static files.
    Args:
        number (Any): The number of archives to keep.
    """
    archives = os.listdir('versions/')
    archives.sort(reverse=True)
    start = int(number)
    if not start:
        start += 1
    if start < len(archives):
        archives = archives[start:]
    else:
        archives = []
    for archive in archives:
        os.unlink('versions/{}'.format(archive))
    cmd_parts = [
        "rm -rf $(",
        "find /data/web_static/releases/ -maxdepth 1 -type d -iregex",
        " '/data/web_static/releases/web_static_.*'",
        " | sort -r | tr '\\n' ' ' | cut -d ' ' -f{}-)".format(start + 1)
    ]
    run(''.join(cmd_parts))
