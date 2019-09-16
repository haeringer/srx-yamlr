import os

GIT_SERVER = os.environ.get("YM_GITSERVER", "")
REMOTE_REPO = os.environ.get("YM_ANSIBLEREPO", "")
REMOTE_REPO_URL = os.path.join(GIT_SERVER, REMOTE_REPO)
