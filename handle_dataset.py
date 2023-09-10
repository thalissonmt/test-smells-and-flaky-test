import csv
from utils import Utils

def filterTestsWithAcceptedFix(dataset_path, output_path):
    try:
        with open(dataset_path, 'rt', encoding='UTF8') as inputFile:
            print("Filtering dataset...")
            csv_reader_object = csv.reader(inputFile)
            # The line will skip the first row of the csv file (Header row)
            next(csv_reader_object) 
            handled_data = list()
            for row in csv_reader_object: 
                if row[5] == 'Accepted':
                    handled_data.append(row)

        Utils.writeCsvFile(output_path, handled_data)

    except Exception as e:
        print(f'Error on filterTestWithAcceptedFix: {e}')

def removeRepositoriesWithError(dataset_path, output_path, repositories_error_path):
    repositories_error = Utils.readJsonFile(repositories_error_path)
    urls_error = [d['url'] for d in repositories_error]  
    with open(dataset_path, 'rt', encoding='UTF8') as inputFile, open(output_path, 'wt', encoding='UTF8', newline='') as outputFile:
            writer = csv.writer(outputFile)
            for row in csv.reader(inputFile):
                url = row[0]
                if url not in urls_error:
                     writer.writerow(row)
