from concurrent.futures import wait, ThreadPoolExecutor
from os import walk, chmod
from os.path import join
from stat import S_IRWXU
from shutil import rmtree

from git import Repo  # GitPython
from requests import Session  # requests
from github import Github  # PyGithub



try:
    import env
    github_username = env.github_username
    github_password = env.github_password
    github_access_token = env.github_access_token
    github_organization = env.github_organization

    bitbucket_username = env.bitbucket_username
    bitbucket_password = env.bitbucket_password
    bitbucket_workspace = env.bitbucket_workspace
except [ImportError, AttributeError]:
    exit(f'Failed to load attributes from env.py. Please ensure you follow the steps in the readme. Closing')


GITHUB_SESSION = Session()
GITHUB_SESSION.auth = (github_username, github_password)
GITHUB_API_URL = "https://api.github.com"

BITBUCKET_SESSION = Session()
BITBUCKET_SESSION.auth = (bitbucket_username, bitbucket_password)
BITBUCKET_API_URL = "https://api.bitbucket.org/2.0"

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}


def confirm_bitbucket_access() -> bool:
    url = f'{BITBUCKET_API_URL}/workspaces/{bitbucket_workspace}'
    r = BITBUCKET_SESSION.get(url, headers=headers)
    if r.status_code == 200:  # Successfully loads workspace details
        return True
    return False

def confirm_bitbucket_project() -> bool:
    payload = {'name': 'Github Migration',
               'key': 'MIGRATION',
               'is_private': True,
               'description': 'Repositories Migrated from Github to Bitbucket'
               }
    url = f'{BITBUCKET_API_URL}/workspaces/{bitbucket_workspace}/projects'
    r = BITBUCKET_SESSION.post(url, headers=headers, json=payload)
    if r.status_code == 201 or "Project with this Name" in r.text:  # Created new or already exists
        return True
    return False

def get_github_organization_repos():
    g = Github(github_access_token)
    org = g.get_organization(github_organization)
    repos = org.get_repos()

    for repo in repos:
        print(f'Located "{repo.name}", starting to clone.') #repo.name
        yield repo.name, repo.clone_url

def get_github_personal_repos(page=None):
    if page is None:
        page = 1
    params = {'per_page': 100, 'page': page, 'type': 'all'}
    if github_organization == "":
        # If repos exist under user
        url = f'{GITHUB_API_URL}/users/{github_username}/repos'
    else:
        # if repos exist under org
        url = f'{GITHUB_API_URL}/orgs/{github_organization}/repos'
    r = GITHUB_SESSION.get(url, headers=headers, params=params)
    if r.json(): # if content in list
        for repo in r.json():
            yield repo.get('name'), repo.get('clone_url')
        page += 1
    else:
        # empty page result so no repos remaining
        return

def create_bitbucket_repo(repo_name) -> bool:
    payload = {'scm': 'git',
               'is_private': True,
               'project': {'key': 'MIGRATION'},
               }
    url = f'{BITBUCKET_API_URL}/repositories/{bitbucket_workspace}/{repo_name}'
    r = BITBUCKET_SESSION.post(url, headers=headers, json=payload)
    if r.status_code in [200, 201]:  # Created Successfully
        return True
    elif r.status_code in [400]:
        if "already has a repository with this name" in r.text: # repo already exists
            return True
    return False

def clone_push(repo_name, clone_url, push_url):
    staging_dir = f"./temp-{repo_name}"
    cloned_repo = Repo.clone_from(clone_url, staging_dir, mirror=True)
    new_origin = cloned_repo.create_remote("bitbucket", push_url)
    new_origin.push(all=True)
    new_origin.push(tags=True)
    try:
        # ensure script has perms over file path before deleting
        for root, dirs, files in walk(staging_dir):
            for d in dirs:
                chmod(join(root, d), S_IRWXU)
            for f in files:
                chmod(join(root, f), S_IRWXU)
        # recusrively delete temp directory for this repo
        rmtree(staging_dir)
    except OSError as e:
        print(f'Unable to delete "{staging_dir}" automatically. Manual cleanup is necessary.\n{e.strerror}')

def main():
    git_tasks = []
    executor = ThreadPoolExecutor()

    if not confirm_bitbucket_access():
        exit(f'Access to Bitbucket could not be confirmed for the workspace "{bitbucket_workspace}".'
             '\nPlease confirm the credentials provided and try again.')

    if not confirm_bitbucket_project():
        exit('Access to the Bitbucket workspace succeeded but the script was unable to create the staging project "Github Migration" for some reason.'
             '\nPlease verify credential permissions and try again.')

    if github_organization != "":
        for repo_name, github_clone_url in get_github_organization_repos():
                print(f'Migrating "{repo_name}" from Github to Bitbucket...')
                bitbucket_repo_name = repo_name.lower().replace(' ', '_')
                create_bitbucket_repo(bitbucket_repo_name)
                bitbucket_push_url = f'https://{bitbucket_username}@bitbucket.org/{bitbucket_workspace}/{bitbucket_repo_name}.git'
                git_tasks.append(executor.submit(clone_push, repo_name, github_clone_url, bitbucket_push_url))
    else:  
        for repo_name, github_clone_url in get_github_personal_repos():
                print(f'Migrating "{repo_name}" from Github to Bitbucket...')
                bitbucket_repo_name = repo_name.lower().replace(' ', '_')
                create_bitbucket_repo(bitbucket_repo_name)
                bitbucket_push_url = f'https://{bitbucket_username}@bitbucket.org/{bitbucket_workspace}/{bitbucket_repo_name}.git'
                git_tasks.append(executor.submit(clone_push, repo_name, github_clone_url, bitbucket_push_url))

    wait(git_tasks)


if __name__ == '__main__':
    main()
