import os
import csv
from git import Repo, RemoteProgress
from utils import Utils
from tqdm import tqdm


class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


def getRespositoriesUrl(dataset_path):
    try:
        with open(dataset_path, 'rt', encoding='UTF8') as inputFile:
            repo_infos = dict()
            for row in csv.reader(inputFile):
                repo_infos[row[0]] = row[1]

            return list(repo_infos)
    except Exception as e:
        print(f'Error on getRespositoriesUrl: {e}')
        return list()


def cloneRepositories(dataset_path, repositories_path, repositories_error_path):
    repositories = getRespositoriesUrl(dataset_path)
    repository_length = len(repositories)
    if repository_length == 0:
        print('No repository found')
        return

    print('Cloning ', repository_length, ' repositories to directory "' +
          repositories_path + '". Please wait...')
    repositories_error = list()
    for idx, repo_url in enumerate(repositories):
        Utils.progress(idx + 1, repository_length)
        path_name = Utils.getRepositoryPathFromGitUrl(repositories_path, repo_url)
        try:
            if not os.path.exists(path_name) or len(os.listdir(path_name)) <= 2:
                print('Clonning', path_name, '...')
                Repo.clone_from(repo_url, path_name, progress=CloneProgress())

        except Exception as e:
            repositories_error.append({"url": repo_url, "path": path_name, "error": str(e)})

    Utils.writeJsonFile(repositories_error_path, repositories_error)
    successfully_cloned = len(repositories) - len(repositories_error)
    print(f'\nSuccessfully cloned {successfully_cloned} repositories!')

def gitCheckoutToParent(repository_path, commit_sha) -> str:
    repo = Repo(repository_path)
    repo.git.checkout(commit_sha)
    parent = repo.head.commit.parents[0]
    repo.git.checkout(parent.hexsha)
    return parent.hexsha

def gitCheckout(repository_path, commit_sha):
    repo = Repo(repository_path)
    repo.git.checkout(commit_sha)
