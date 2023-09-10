from utils import Utils
from result_analyzer import generateResult
from moss_script import getMossResult


def getOutputTsDetectorPaths():
    ts_detector_output_prefix = 'Output_TestSmellDetection_'
    filenames = Utils.getFilenames('./')
    timestamp_list = list()
    for filename in filenames:
        if ts_detector_output_prefix in filename:
            timestamp = int(''.join(filter(str.isdigit, filename)))
            timestamp_list.append(timestamp)

    timestamp_list.sort()

    if len(timestamp_list) > 1:
        ts_detector_output_fix = f'./{ts_detector_output_prefix}{timestamp_list[-2]}.csv'
        ts_detector_output_flakiness = f'./{ts_detector_output_prefix}{timestamp_list[-1]}.csv'
        return (ts_detector_output_fix, ts_detector_output_flakiness)

    return (None, None)


def main():
    result_path = './result.csv'
    moss_path = './moss.pl'
    override_moss_url = False

    ts_detector_output_fix, ts_detector_output_flakiness = getOutputTsDetectorPaths()

    if ts_detector_output_fix and ts_detector_output_flakiness:
        generateResult(ts_detector_output_flakiness, ts_detector_output_fix, result_path)
        getMossResult(result_path, moss_path, override_moss_url)


if __name__ == "__main__":
    main()
