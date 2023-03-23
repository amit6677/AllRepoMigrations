
## Purpose
This tool is intended to locate and migrate repositories stored on Github to Bitbucket Cloud. It itterates through the [Github API](https://docs.github.com/en/rest/overview) and as it locates your source repos, it will create an empty repo within Bitbucket in the project "Github Migration" (with a key of "MIGRATION") and then the script will multi-thread out git operations to clone and then push the repo from Github to Bitbucket as if performing the following git actions:

    git clone <repo> --mirror
    git remote add bitbucket <bitbucket-url>
    git push -u bitbucket --all
    git push -u bitbucket --tags

After the push is completed, the local clone will be deleted, freeing up the thread for the next clone.

## Usage

 ### To execute the code you have to add these details in the env.py file.
 ### owner, github_username, github_password and github_access_token from github and bitbucket_username, bitbucket_password, and bitbucket_workspace from Bitbucket 
 ### token generation steps are given above
'''


> 1) If an organization is provided within the env, the api query will be [targeted at the provided org](https://docs.github.com/en/rest/reference/repos#list-organization-repositories) rather than at the [user's repo listing](https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user). Use this arguement accordingly.
> 2) **Note**: When filling out the "password" variable, you will need to use a [Bitbucket Cloud App Password|https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/] and a [Github access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) respectively. This password/token is only used to interact with the api and the git operations will attempt to utilize your git credential manager's cached credentials.

Next, you will need to install the dependencies for the script ([GitPython](https://gitpython.readthedocs.io/en/stable/intro.html) and [Requests](https://docs.python-requests.org/en/master/)) by either using the requirements.txt or by installing the packages by hand.

Configure a python virtual environment and install package dependencies with the follow commands:

        python3 -m venv venv
        source venv/Scripts/activate  # If using gitbash on Windows
        source venv/bin/activate      # If on linux/mac
        pip3 install -r requirements.txt

Once the dependencies are satisfied and you have provided your unique details, simply run the script with Python  It should print a line, for each repo processed/migrated, stating the repo name from Github. To run script with python via:

        python3 import.py

### Note
This script attempts to clone and push to both platforms via HTTPS, please ensure that your git credential manager is already aware of your credentials to both hosts before hand by performing a clone or push to both platforms with a test repo before proceeding with this script.
