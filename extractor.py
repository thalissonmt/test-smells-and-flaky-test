import csv
import requests
import time
from utils import Utils
from bs4 import BeautifulSoup

def extractShaFromPR(dataset_path, output_path, extraction_error_path):
    with open(dataset_path, 'rt', encoding='UTF8') as inputFile:
        print("Extracting SHA from PR...")
        result = list()
        csv_reader = csv.reader(inputFile)
        length = Utils.getCsvLength(dataset_path)
        extraction_errors = list()
        for idx, row in enumerate(csv_reader):
            url = row[6]
            commit_sha = ''
            Utils.progress(idx+1, length)

            # checks if the last PR is the same as the current PR
            if result and result[-1][6] == url:
                commit_sha = result[-1][7]
                row.insert(7, commit_sha)
                result.append(row)
                continue
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    if soup.select('span[class="State State--merged"]'): #checks if PR state is Merged
                        elements = soup.select('div[class="TimelineItem-body"] > a > code[class^="Link--primary text-bold"]')
                        commit_sha = elements[0].text
                    elif soup.select('span[class="State State--closed"]'): #checks if PR state is Closed
                        elements = soup.select('div[class="TimelineItem-body"] > code > a[data-hovercard-type^="commit"]')
                        commit_sha = elements[0].text

                if commit_sha:
                    print(url, commit_sha)
                    row.insert(7, commit_sha)
                    result.append(row)
                else:
                    extraction_errors.append({"url": url, "error": "SHA not found"})

            except Exception as e:
                extraction_errors.append({"url": url, "error": str(e)})
                print('url', url, 'extract exception', e)
            
            time.sleep(0.2)

        Utils.writeCsvFile(output_path, result)
        Utils.writeJsonFile(extraction_error_path, extraction_errors)