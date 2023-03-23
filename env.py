'''
Github admin level username and password
This is used to interact with the github api to collect the existing repo details
and to perform git clone operations via HTTPS before pushing to Bitbucket Cloud.
'''
github_username = "xxxxxx"
github_password = "xxxxxx"
github_access_token = "xxxxxx"
github_organization = "xxxxxx"  # If populated, will only retrieve org repos and not personal repos


'''
Bitbucket admin level username and password
This is used to interact with the Bitbucket api to create a project "github_migration" and
then the individual empty repos within Bitbucket to then push the cloned github repos into.
'''
bitbucket_username = "xxxxxx"
bitbucket_password = "xxxxxx"
bitbucket_workspace = "xxxxxx"  # The name (found as part of the URL) for the workspace that you would like your github repos to be imported into.
