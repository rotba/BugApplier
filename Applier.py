import os
import git
from mvnpy import bug as mvn_bug
from mvnpy import Repo
import copy

DATABASE = r'C:\BugsDB'

class Applier(object):

    def __init__(self, project_url, path):
        self._path = path
        proj_name = project_url.rsplit('/', 1)[1]
        self._data_handler = mvn_bug.Bug_data_handler(os.path.join(DATABASE, proj_name + '\\data'))
        git.Git(self._path).init()
        try:
            git.Git(self._path).clone(project_url)
        except git.exc.GitCommandError as e:
            if 'already exists and is not an empty directory.' in str(e):
                pass
        self._repo = git.Repo(os.path.join(self._path, proj_name))
        self._mvn_repo = Repo.Repo(os.path.join(self._path, proj_name))

    #Applies the bug on the project
    def apply(self, bug):
        self._repo.git.add('.')
        self._repo.git.clean('-f')
        buggy_commit = bug.parent
        patch_path = self.data_handler.get_patch(bug)
        self._repo.git.checkout(buggy_commit, '-f')
        if bug.type == mvn_bug.Bug_type.GEN:
            self._mvn_repo.setup_tests_generator()
        self._repo.git.execute(['git', 'apply', patch_path])
        if bug.type == mvn_bug.Bug_type.GEN:
            self.apply_generated_test_env(bug)

    # Gets all the bugs in issue_key/commit_hexsha
    def get_bugs(self, issue_key, commit_hexsha):
        return self.data_handler.get_bugs(issue_key, commit_hexsha)

    def apply_generated_test_env(self, bug):
        scaffolding_file_path = self.data_handler.get_scaffolding_dir(bug)
        file_patch_path = self.data_handler.get_file_patch(scaffolding_file_path)
        self._repo.git.execute(['git', 'apply', file_patch_path])

    @property
    def data_handler(self):
        return self._data_handler

    @property
    def proj_dir(self):
        return self._repo.git_dir.strip('.git')


