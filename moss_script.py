import csv
import subprocess
import re
import requests
from utils import Utils
from bs4 import BeautifulSoup

def runMoss(moss_path: str, path1: str, path2: str) -> str:
    compile_command = f'perl {moss_path} -l java {path1} {path2}'
    try:
        print("Waiting for response.")
        output = subprocess.check_output(compile_command, shell= True).decode("utf-8")
        if output:
            url = re.search("(?P<url>https?://[^\s]+)", output).group("url")
    except Exception as e:
        print('runMoss error', e)
        return ''
    
    print("URL", url)
    return url

def extractScore(text: str) -> str:
    score = re.search("(\d+%)", text)
    if not score:
        return ''
    return score.group(1)

def getMossScore(url: str) -> tuple[str, str]:
    if not url:
        return ('', '')
    try:
        print("Extracting Score from", url)
        test_score = ''
        fix_score = ''
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            elements = soup.select('tr > td > a')
            length = len(elements)
            if length > 0:
                test_score = extractScore(elements[0].text)
            if length > 1:
                fix_score = extractScore(elements[1].text)
            
            return (test_score, fix_score)

    except Exception as e:
        print('getMossScore error', 'url', url, 'extract exception', e)
        return ('', '')

def getMossResult(result_path: str, moss_path: str, override = False):
    with open(result_path, 'tr', encoding='UTF8') as inputFile:
        csv_reader = csv.reader(inputFile)

        header = next(csv_reader)
        header.insert(28, "MOSS Result")
        header.insert(29, "MOSS Test Score")
        header.insert(30, "MOSS Fix Score")
        header = header[:31]

        length = Utils.getCsvLength(result_path)
        result = list()
        for idx, row in enumerate(csv_reader):
            try:
                moss_url = row[28]
            except:
                moss_url = None
            Utils.progress(idx+1, length)
            print('')

            if moss_url and not override:
                test_score, fix_score = getMossScore(moss_url)
                row.insert(29, test_score)
                row.insert(30, fix_score)
                row = row[:31]
                result.append(row)
                continue
            
            path1 = row[2]
            path2 = row[4]
            moss_url = runMoss(moss_path, path1, path2)
            row.insert(28, moss_url)

            test_score, fix_score = getMossScore(moss_url)
            row.insert(29, test_score)
            row.insert(30, fix_score)
            row = row[:31]

            result.append(row)

        result.insert(0, header)
        Utils.writeCsvFile(result_path, result)