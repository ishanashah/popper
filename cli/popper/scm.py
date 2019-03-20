import os
import popper.utils as pu


def get_root_folder(debug=False):
    """Tries to find the root folder,
    """
    return pu.exec_cmd('git rev-parse --show-toplevel', debug=debug)[0]


def infer_repo_name_from_root_folder(debug=False):
    """Finds the root folder of a local Github repository and returns it.

    Returns:
        repo_name (str): the name of the root folder.
    """
    root_folder = get_root_folder(debug)
    repo_name = os.path.basename(root_folder)
    return repo_name


def get_name(debug):
    """Assuming $PWD is part of a Git repository, it tries to find the name of
    the repository by looking at the 'origin' git remote. If no 'origin' remote
    is defined, it returns the name of the parent folder.
    """
    url = get_remote_url(debug)

    if not url:
        return infer_repo_name_from_root_folder()

    if url.endswith('.git'):
        url = url[:-4]

    return os.path.basename(url)


def get_user(debug):
    """Assuming $PWD is part of a Git repository, it tries to find the user (or
    org) of the repository, as specified in the 'origin' git remote
    information. If the repository has not been pushed to a remote repo or if
    'origin' is not the name of any remote repository, returns None.
    """
    url = get_remote_url(debug)
    if url:
        if 'https://' in url:
            return os.path.basename(os.path.dirname(url))
        else:
            return url.split(':')[1]

    return None


def get_ref(debug):
    """Returns the Git REF pointed by .git/HEAD"""
    r = get_root_folder(debug)
    cmd = "cat {}/.git/HEAD | awk '{{print $2}}'".format(r)
    return pu.exec_cmd(cmd, debug=debug)[0]


def get_sha(debug):
    """Runs git rev-parse --short HEAD and returns result"""
    return pu.exec_cmd('git rev-parse --short HEAD', debug=debug)[0]


def get_remote_url(debug=False):
    """Obtains remote origin URL, if possible. Otherwise it returns empty str.
    """
    url, _ = pu.exec_cmd('git config --get remote.origin.url', debug=debug,
                         ignore_error=True)

    # cleanup the URL so we get in in https form and without '.git' ending
    if url.endswith('.git'):
        url = url[:-4]
    if 'git@' in url:
        url = 'https://' + url[4:].replace(':', '/')

    return url


def clone(url, org, repo, repo_parent_dir, version=None, debug=False):
    """Clones a repository using Git. The URL for the repo is
    https://github.com/ by default. To override this, other URLs can be given
    by defining them in the 'action_urls' list specified in the .popper.yml
    file.
    """
    repo_dir = os.path.join(repo_parent_dir, repo)
    if os.path.exists(repo_dir):
        pu.exec_cmd('rm -rf {}'.format(repo_dir), debug=debug)

    if '@' in url:
        url += ':'
    else:
        url += '/'

    cmd = 'git -C {} clone --depth=1 {}{}/{} {}'.format(
        repo_parent_dir,
        url,
        org,
        repo.split('@')[0],
        repo,
    )
    pu.exec_cmd(cmd, debug=debug)

    if not version:
        return

    pu.exec_cmd('git -C {} checkout {}'.format(repo_dir, version), debug=debug)