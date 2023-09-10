import os
import csv
from utils import Utils
from git_functions import gitCheckout, gitCheckoutToParent
import shutil


errors = list()
output_fixes_path = './output/fixes'
output_flakiness_path = './output/flakiness'


from enum import Enum
 
class TestType(Enum):
    FIX = 1
    FLAKINESS = 2


class TestError:
    def __init__(self, url, commit, test_path, reason, error):
        self.url = url
        self.commit = commit
        self.where = reason
        self.test_path = test_path
        self.error = error


def testErrorToDict(error: TestError):
    return {
        'url': error.url,
        'commit': error.commit,
        'test_path': error.test_path,
        'where': error.where,
        'error': error.error,
    }


def findTestPath(repo_path, test: str):
    test_name = test.split('.')[-2] + '.java'
    test_path = test.rsplit('.', 1)[0]  # Remove the test name
    test_path = test_path.replace('.', os.sep) + '.java'
    finded_path = ''
    for dirpath, dirnames, filenames in os.walk(f'{repo_path}/'):
        for filename in filenames:
            if filename == test_name:
                filename = os.path.join(dirpath, filename)
                filename = os.path.abspath(filename)
                finded_path = filename
                if test_path in filename:
                    return filename, True
    return finded_path, False


def getPath(data: list, repository_path: str, sha: str, type: TestType):
    url = data[0]
    test = data[3]
    flow = type.name.lower
    
    if type == TestType.FIX:
        dir_path = output_fixes_path
    else:
        dir_path = output_flakiness_path

    try:
        if type == TestType.FLAKINESS:
            sha = gitCheckoutToParent(repository_path, sha)
        else:
            gitCheckout(repository_path, sha)
    except Exception as e:
        errors.append(TestError(url, sha, '', f'{flow} checkout', str(e)))
        return ''
    
    new_test_name = f"{test.split('.')[-2]}_{sha}.java"
    new_test_path = dir_path + '/' + new_test_name

    if os.path.exists(new_test_path):
        return new_test_path

    path, is_correct = findTestPath(repository_path, test)
    if not is_correct:
        errors.append(TestError(url, sha, path, f'{flow} path', ''))
        return ''

    try:
        new_path = shutil.copy(path, new_test_path)
        return new_path
    except Exception as e:
        errors.append(TestError(url, sha, path, f'{flow} copy', str(e)))
        return ''


def generateTsDetectorInput(dataset_path, repositories_path, input_fix_path, input_flakiness_path):
    Utils.createFolder(output_fixes_path)
    Utils.createFolder(output_flakiness_path)
    num_rows = Utils.getCsvLength(dataset_path)
    with open(dataset_path, 'tr', encoding='UTF8') as inputFile:
        print('Finding tests and fixes files path. Please wait...')

        idx = 0
        ts_detector_input_fix = list()
        ts_detector_input_flakiness = list()

        for row in csv.reader(inputFile):
            idx = idx + 1
            Utils.progress(idx, num_rows)

            url = row[0]
            fix_sha = row[7]
            repo_path = Utils.getRepositoryPathFromGitUrl(repositories_path, url)

            fix_path = getPath(row, repo_path, fix_sha, TestType.FIX)
            if not fix_path:
                continue
            fix_path = os.path.abspath(fix_path)
            if any(fix_path in path for path in ts_detector_input_fix):
                continue

            flakiness_path = getPath(row, repo_path, fix_sha, TestType.FLAKINESS)
            if not flakiness_path:
                continue
            flakiness_path = os.path.abspath(flakiness_path)

            project_name = repo_path.removeprefix(f'{repositories_path}/')
            ts_detector_input_fix.append([project_name, fix_path])
            ts_detector_input_flakiness.append([project_name, flakiness_path])

        Utils.writeCsvFile(input_fix_path, ts_detector_input_fix)
        Utils.writeCsvFile(input_flakiness_path, ts_detector_input_flakiness)
        Utils.writeJsonFile('./output/input_generate_errors.json', list(map(testErrorToDict, errors)))
