from utils import Utils
import csv

def generateValues(path):
    with open(path, 'rt', encoding='UTF8') as inputFile:
        output_list = list()
        csv_reader = csv.reader(inputFile)
        first_row = next(csv_reader)
        for row in csv_reader:
            output_list.append(row)
        
        return output_list, first_row

def generateResult(ts_detector_output, ts_detector_output_fix, result_path):   
    test_result, header = generateValues(ts_detector_output)
    fix_result, _ = generateValues(ts_detector_output_fix)

    result = list()
    total_reduction = [0] * 23
    total_increase = [0] * 23
    for test_row, fix_row in zip(test_result, fix_result):
        result_row = list()
        row_reduction = 0
        row_increase = 0
        total_index = 0
        for test_value, fix_value in zip(test_row[7:], fix_row[7:]):
            if test_value and fix_value:
                result_value = int(test_value) - int(fix_value)
                if(result_value > 0):
                    row_reduction = row_reduction + result_value
                    total_reduction[total_index] += result_value
                else:
                    row_increase = row_increase + abs(result_value)
                    total_increase[total_index] += abs(result_value)
                result_row.append(result_value)
            else:
                result_row.append(0)
                total_reduction[total_index] += 0
                total_increase[total_index] += 0
            total_index += 1
        if row_reduction > 0 or row_increase > 0:
            result_row.append(row_reduction)
            total_reduction[total_index] += row_reduction
            total_index += 1

            result_row.append(row_increase)
            total_increase[total_index] += row_increase

            result_row.insert(0, test_row[0]) #App
            result_row.insert(1, test_row[1]) #TestClass
            result_row.insert(2, test_row[2]) #TestFilePath
            result_row.insert(3, fix_row[1]) #FixClass
            result_row.insert(4, fix_row[2]) #FixFilePath
            result.append(result_row)

    header = header[7:]
    header.append('Total Reduction')
    header.append('Total Increase')
    header.insert(0, 'App') 
    header.insert(1, 'TestClass') 
    header.insert(2, 'TestFilePath') 
    header.insert(3, 'FixClass') 
    header.insert(4, 'FixFilePath') 
    result.insert(0, header)

    total_reduction.insert(0, 'Total Reduction') 
    total_reduction.insert(1, '-') 
    total_reduction.insert(2, '-') 
    total_reduction.insert(3, '-') 
    total_reduction.insert(4, '-') 
    result.append(total_reduction)

    total_increase.insert(0, 'Total Increase') 
    total_increase.insert(1, '-') 
    total_increase.insert(2, '-') 
    total_increase.insert(3, '-') 
    total_increase.insert(4, '-') 
    result.append(total_increase)
    
    Utils.writeCsvFile(result_path, result)