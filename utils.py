import os
import re
import json
import csv
import sys
import errno


class Utils:

    @staticmethod
    def readFile(path) -> str:
        newPath = os.path.join(os.path.dirname(
            __file__), path)
        with open(newPath, 'r', encoding='utf-8') as f:
            data = f.read()
        return data

    @staticmethod
    def regexSearch(pattern, page) -> str:
        try:
            result = re.search(pattern, page).group(1)
        except:
            result = ''
        return result

    @staticmethod
    def getFilenames(path) -> list:
        newPath = os.path.join(os.path.dirname(__file__), path)
        filenames = next(os.walk(newPath), (None, None, []))[2]
        return filenames

    @staticmethod
    def readJsonFile(path):
        jsonPath = os.path.join(os.path.dirname(
            __file__), path)
        with open(jsonPath, encoding='utf-8') as f:
            jsonData = json.load(f)
        return jsonData

    @staticmethod
    def writeJsonFile(path, obj):
        jsonPath = os.path.join(os.path.dirname(
            __file__), path)
        with open(jsonPath, "w", encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False)

    @staticmethod
    def writeCsvFile(path, obj):
        csvPath = os.path.join(os.path.dirname(
            __file__), path)
        with open(csvPath, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(obj)
    
    @staticmethod
    def getCsvLength(path):
        with open(path, 'rt', encoding='UTF8') as inputFile:
            csv_reader = csv.reader(inputFile)
            length = sum(1 for row in csv_reader)
        return length

    @staticmethod
    def progress(count, total, status=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = "=" * filled_len + "-" * (bar_len - filled_len)

        sys.stdout.write("[%s] %s%%%s\r" % (bar, percents, status))
        sys.stdout.flush()

    @staticmethod
    def createFolder(path):
        try:
            os.mkdir(path)
            return path
        except OSError as e:
            if e.errno == errno.EEXIST:
                return path
            else:
                raise
    
    @staticmethod
    def getRepositoryPathFromGitUrl(repositories_path, git_url):
        url_split = git_url.split('/')
        organization_name = url_split[-2]
        project_name = url_split[-1].split('.git')[0]
        return f'{repositories_path}/{organization_name}/{project_name}'
