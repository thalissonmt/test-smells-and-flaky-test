from git_functions import cloneRepositories
from input_generator import generateTsDetectorInput
from extractor import extractShaFromPR
from utils import Utils
from subprocess import call, run
import handle_dataset


def runTSDetect(ts_detector_input):
    compile_command = f'java -jar TestSmellDetector.jar {ts_detector_input}'
    if call(compile_command, shell=True) == 0:
        print("TSDetect run successful!")
    else:
        print("compilation unsuccessful! aborting")

def main():
    output_dir = './output'
    dataset_path = './pr-data.csv'
    repositories_path = './repositories'

    repositories_error_path = f'{output_dir}/repositories_error.json'
    extraction_errors_path = f'{output_dir}/extraction_errors.json'
    
    filtered_data_path = f'{output_dir}/data-filtered.csv'
    handled_data_path = f'{output_dir}/data-handled.csv'
    extract_data_path = f'{output_dir}/data-extracted.csv'
    ts_detector_input_fix = f'{output_dir}/ts-detector-input-fix.csv'
    ts_detector_input_flakiness = f'{output_dir}/ts-detector-input-flakiness.csv'
    
    Utils.createFolder(output_dir)
    Utils.createFolder(repositories_path)

    handle_dataset.filterTestsWithAcceptedFix(dataset_path, filtered_data_path)

    cloneRepositories(filtered_data_path, repositories_path, repositories_error_path)

    handle_dataset.removeRepositoriesWithError(filtered_data_path, handled_data_path, repositories_error_path)

    extractShaFromPR(handled_data_path, extract_data_path, extraction_errors_path)

    generateTsDetectorInput(extract_data_path, repositories_path, ts_detector_input_fix, ts_detector_input_flakiness)

    runTSDetect(ts_detector_input_fix)
    runTSDetect(ts_detector_input_flakiness)

    run(["python", "main_result.py"])

if __name__ == "__main__":
    main()