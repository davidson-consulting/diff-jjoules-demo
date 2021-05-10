import os
import csv
import json
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from shutil import rmtree

def run_cmd(command):
    print(command)
    os.system(command)

def delete_directory(directory):
    if os.path.isdir(directory):
        rmtree(directory)

def git_clone_folder(folder):
    run_cmd(
        ' '.join([
                'git',
                'clone',
                'https://github.com/davidson-consulting/diff-jjoules-demo.git', 
                folder
        ])
    )

def git_reset_hard_folder(folder, sha):
    cwd = os.getcwd()
    os.chdir(folder)
    run_cmd(' '.join([
        'git',
        'reset',
        '--hard',
        sha
    ]))
    os.chdir(cwd)

MVN_CMD_WITH_SKIPS_F = 'mvn -Drat.skip=true -Djacoco.skip=true -Danimal.sniffer.skip=true -f '
POM_FILE = '/pom.xml'
CLEAN_GOAL = 'clean'
INSTALL_GOAL = 'install'
TEST_GOAL = 'test'
SKIP_TESTS = '-DskipTests'
OPT_TEST = '-Dtest='

def mvn_install_skip_test_build_classpath(path):
    return run_cmd(' '.join([
        MVN_CMD_WITH_SKIPS_F,
        path + POM_FILE,
        CLEAN_GOAL,
        INSTALL_GOAL,
        SKIP_TESTS,
        'dependency:build-classpath',
        '-Dmdep.outputFile=classpath'
    ]))

CMD_DIFF_TEST_SELECTION = 'eu.stamp-project:dspot-diff-test-selection:3.1.1-SNAPSHOT:list'
OPT_PATH_DIR_SECOND_VERSION = '-Dpath-dir-second-version='

def mvn_diff_test_selection(path_first_version, path_second_version):
    return run_cmd(
         ' '.join([
            MVN_CMD_WITH_SKIPS_F,
            path_first_version + POM_FILE,
            CLEAN_GOAL,
            CMD_DIFF_TEST_SELECTION,
            '-Dpath-dir-second-version=' + path_second_version,
        ])
    )

def mvn_clean_test_skip_test(path):
    return run_cmd(' '.join([
        MVN_CMD_WITH_SKIPS_F,
        path + POM_FILE,
        CLEAN_GOAL,
        TEST_GOAL,
        SKIP_TESTS
    ]))

def get_tests_to_execute(path):
    tests_to_execute = {}
    with open(path, 'r') as csvfile:
        file = csv.reader(csvfile, delimiter=';')
        for line in file:
            tests_to_execute[line[0]] = line[1:]
    return tests_to_execute

CMD_DIFF_INSTRUMENT = 'fr.davidson:diff-jjoules:instrument'
OPT_CP_V2 = '-Dclasspath-path-v2=classpath'
OPT_CP_V1 = '-Dclasspath-path-v1=classpath'
OPT_VALUE_TEST_LISTS = '-Dtests-list=testsThatExecuteTheChange.csv'

def mvn_diff_jjoules_instrument(path_v1, path_v2):
    return run_cmd(
         ' '.join([
            MVN_CMD_WITH_SKIPS_F,
            path_v1 + POM_FILE,
            CLEAN_GOAL,
            TEST_GOAL,
            SKIP_TESTS,
            CMD_DIFF_INSTRUMENT,
            OPT_VALUE_TEST_LISTS,
            '-Dpath-dir-second-version=' + path_v2,
            OPT_CP_V2,
            OPT_CP_V1,
        ])
    )

def mvn_test(path, tests_to_execute):
    return run_cmd(
        ' '.join([
            MVN_CMD_WITH_SKIPS_F,
            path + POM_FILE,
            TEST_GOAL,
            OPT_TEST + ','.join([test + '#' + '+'.join(tests_to_execute[test]) for test in tests_to_execute]),
            '--quiet'
        ])
    )

def read_json(path_to_json):
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    return data

def mediane_of_delta(data_v1, data_v2):
    deltas = []
    for i in range(len(data_v1)):
        deltas.append(data_v2[i] - data_v1[i])
    return mediane(deltas)

def mediane_delta(data_v1, data_v2):
    return mediane(data_v2) - mediane(data_v1)

def mediane(data):
    data = sorted(data)
    if len(data) % 2 == 0:
        middle_cursor = int(len(data) / 2)
        print(middle_cursor, len(data), middle_cursor - 1, middle_cursor, data)
        return (data[middle_cursor - 1] + data[middle_cursor]) / 2
    else:
        return data[int(len(data)/2)]

def quartiles(data):
    data = sorted(data)
    if len(data) % 2 == 0:
        cursor_middle = int(len(data) / 2)
        return mediane(data[:cursor_middle]), mediane(data[cursor_middle:])
    else:
        cursor_end_q1 = int((len(data) / 2) - 1)
        cursor_begin_q3 = int((len(data) / 2) + 1)
        return mediane(data[:cursor_end_q1]), mediane(data[cursor_begin_q3:])

def write_json(path_to_json, data):
    with open(path_to_json, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))

def mkdir(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)

def delete_and_mkdir(directory):
    delete_directory(directory)
    mkdir(directory)

def plot_delta_as_hist2(data_p, data_n, labels, units):
    # print(len(data_p), len(data_n), len(labels), len(units))
    # print(data_p)
    # print(data_n)
    # print(labels)
    # print(units)
    df = pd.DataFrame(
        {
            'Test': labels,
            'Value_n': data_n,
            'Value_p': data_p,
            'Measure': units
        }, 
    )
    #print(df)
    bar_plot = sns.barplot(x="Test", y='Value_p', hue='Measure', data=df)
    bar_plot = sns.barplot(x="Test", y='Value_n', hue='Measure', data=df)

    bar_plot.set_ylabel("Value")
    h, l = bar_plot.get_legend_handles_labels()
    bar_plot.legend(h, [units[0], units[3], units[6]], title="Measurements")
    plt.savefig('target/demo-output/graph.png')
    plt.show()
    plt.clf()

def split_data_array(data):
    data_p, data_n = [], []
    for d in data:
        if d > 0:
            data_p.append(d)
            data_n.append(0)
        else:
            data_n.append(d)
            data_p.append(0)
    return data_p, data_n

def dict_to_array(data):
    return [data[key] for key in data]

def format_perc(value):
    return '{:.2f}'.format(value * float(100)) + '%'

def compute_and_format_perc(med, value):
    return format_perc(float(float(value) / float(med)))

def format(med, value):
    return str(value) + ' (' + compute_and_format_perc(med, value) + ')'

def stats(data_test):
    med = mediane(data_test)
    q1, q3 = quartiles(data_test)
    mean = sum(data_test) / len(data_test)
    deviations = [ (x - mean) ** 2 for x in data_test ]
    variance = sum(deviations) / len(deviations)
    stddev = math.sqrt(variance)
    cv = (q3 - q1) / (q3 + q1)
    qcd = stddev / mean
    return med, format(med, stddev), format_perc(cv), format_perc(qcd)

def do_stats_for_given_measure(key, measure, data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test):
    med, stddev, cv, qcd = stats([d[key] for d in data_per_test])
    mediane_per_test[measure] = med
    stddev_per_test[measure] = stddev
    cv_per_test[measure] = cv
    qcd_per_test[measure] = qcd
    return mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test

def do_all_stats_for_test(data_per_test,mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test):
    mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test = do_stats_for_given_measure('package|uJ', 'Energy', data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test)
    mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test = do_stats_for_given_measure('instructions', 'Instructions', data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test)
    return do_stats_for_given_measure('duration|ns', 'Duration', data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test)

def to_readable_test_name(test):
    return test.split('-')[-1].split('.')[0]

PATH_V1 = '/tmp/v1'
PATH_V2 = '/tmp/v2'

SHA_V1 = '0e1bd12252a970dd41f7e96104db1e24db6ea30d'
SHA_V2 = '8f9690efd14d74065d376a961329ac1a014c887b'

target_jjoules_reports_folder = 'target/jjoules-reports/'

tests = [ 
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapEmptyList.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapOneElement.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapMultipleElement.json'
]

warmup_test_name = 'aaaaa_warmup'

output_demo_directory = 'target/demo-output/'
output_demo_directory_v1 = output_demo_directory + 'v1/'
output_demo_directory_v2 = output_demo_directory + 'v2/'

if __name__ == '__main__':

    # Set up V1
    delete_directory(PATH_V1)
    git_clone_folder(PATH_V1)
    git_reset_hard_folder(PATH_V1, SHA_V1)
    mvn_install_skip_test_build_classpath(PATH_V1)

    # Set up V2
    delete_directory(PATH_V2)
    git_clone_folder(PATH_V2)
    git_reset_hard_folder(PATH_V2, SHA_V2)
    mvn_install_skip_test_build_classpath(PATH_V2)

    # Select tests that execute the changes
    mvn_diff_test_selection(PATH_V1, PATH_V2)
    tests_to_execute_tmp = get_tests_to_execute(PATH_V1 + '/testsThatExecuteTheChange.csv')
    print(tests_to_execute_tmp)
    tests_to_execute = {}
    for test in tests_to_execute_tmp:
        tests_to_execute[test] = []
        print(test)
        for cases in tests_to_execute_tmp[test]:
            print(cases)
            for i in range(5):
                tests_to_execute[test].append('aaa_' + str(i) + '_' + cases)
            tests_to_execute[test].append(cases)
        print(tests_to_execute)
    
    # Cleaning state after test selection
    mvn_clean_test_skip_test(PATH_V2)

    # Instrument the tests that have been selected with diff-jjoules
    mvn_diff_jjoules_instrument(PATH_V1, PATH_V2)
    
    data_per_test_v1 = {}
    data_per_test_v2 = {}

    delete_and_mkdir(output_demo_directory)
    mkdir(output_demo_directory_v1)
    mkdir(output_demo_directory_v2)

    for i in range(0,5):
        mkdir(output_demo_directory_v1 + str(i))
        mkdir(output_demo_directory_v2 + str(i))
        mvn_test(PATH_V1, tests_to_execute)
        mvn_test(PATH_V2, tests_to_execute)
        for test in tests:
            if not test in data_per_test_v1:
                data_per_test_v1[test] = []
                data_per_test_v2[test] = []
            json_v1 = read_json('/'.join([PATH_V1, target_jjoules_reports_folder, test]))
            json_v2 = read_json('/'.join([PATH_V2, target_jjoules_reports_folder, test]))
            print(json_v1)
            print(json_v2)
            data_per_test_v1[test].append(json_v1)
            data_per_test_v2[test].append(json_v2)
            write_json(output_demo_directory_v1 + str(i) + '/' + test, json_v1)
            write_json(output_demo_directory_v2 + str(i) + '/' + test, json_v2)

    mediane_per_test_per_measures_v1 = {}
    stddev_per_test_per_measures_v1 = {}
    cv_per_test_per_measures_v1 = {}
    qcd_per_test_per_measures_v1 = {}
    mediane_per_test_per_measures_v2 = {}
    stddev_per_test_per_measures_v2 = {}
    cv_per_test_per_measures_v2 = {}
    qcd_per_test_per_measures_v2 = {}

    delta_mediane_energy_per_test = {}
    delta_mediane_instr_per_test = {}
    delta_mediane_durations_per_test = {}
    mediane_delta_energy_per_test = {}
    mediane_delta_instr_per_test = {}
    mediane_delta_durations_per_test = {}
    variation_perc_energy_per_test = {}
    variation_perc_instr_per_test = {}
    variation_perc_durations_per_test = {}
    d_variation_perc_energy_per_test = {}
    d_variation_perc_instr_per_test = {}
    d_variation_perc_durations_per_test = {}
    for test in data_per_test_v1:
        mediane_per_test_per_measures_v1[test] = {}
        stddev_per_test_per_measures_v1[test] = {}
        cv_per_test_per_measures_v1[test] = {}
        qcd_per_test_per_measures_v1[test] = {}
        do_all_stats_for_test([d for d in data_per_test_v1[test]], mediane_per_test_per_measures_v1[test], stddev_per_test_per_measures_v1[test], cv_per_test_per_measures_v1[test], qcd_per_test_per_measures_v1[test])

        print(to_readable_test_name(test))
        print('mediane', mediane_per_test_per_measures_v1[test])
        print('stddev', stddev_per_test_per_measures_v1[test])
        print('cv', cv_per_test_per_measures_v1[test])
        print('qcd', qcd_per_test_per_measures_v1[test])

        mediane_per_test_per_measures_v2[test] = {}
        stddev_per_test_per_measures_v2[test] = {}
        cv_per_test_per_measures_v2[test] = {}
        qcd_per_test_per_measures_v2[test] = {}
        do_all_stats_for_test([d for d in data_per_test_v2[test]], mediane_per_test_per_measures_v2[test], stddev_per_test_per_measures_v2[test], cv_per_test_per_measures_v2[test], qcd_per_test_per_measures_v2[test])
        print(to_readable_test_name(test))
        print('mediane', mediane_per_test_per_measures_v2[test])
        print('stddev', stddev_per_test_per_measures_v2[test])
        print('cv', cv_per_test_per_measures_v2[test])
        print('qcd', qcd_per_test_per_measures_v2[test])

        delta_mediane_energy_per_test[test] = mediane_delta(
            [d['package|uJ'] for d in data_per_test_v1[test]],
            [d['package|uJ'] for d in data_per_test_v2[test]]
        )
        mediane_delta_energy_per_test[test] = mediane_of_delta(
            [d['package|uJ'] for d in data_per_test_v1[test]],
            [d['package|uJ'] for d in data_per_test_v2[test]]
        )
        variation_perc_energy_per_test[test] = compute_and_format_perc(
            mediane([d['package|uJ'] for d in data_per_test_v1[test]]),
            delta_mediane_energy_per_test[test], 
        )
        d_variation_perc_energy_per_test[test] = compute_and_format_perc(
            mediane([d['package|uJ'] for d in data_per_test_v1[test]]),
            mediane_delta_energy_per_test[test], 
        )
        delta_mediane_instr_per_test[test] = mediane_delta(
            [d['instructions'] for d in data_per_test_v1[test]],
            [d['instructions'] for d in data_per_test_v2[test]]
        )
        mediane_delta_instr_per_test[test] = mediane_of_delta(
            [d['instructions'] for d in data_per_test_v1[test]],
            [d['instructions'] for d in data_per_test_v2[test]]
        )
        variation_perc_instr_per_test[test] = compute_and_format_perc(
            mediane([d['instructions'] for d in data_per_test_v1[test]]),
            delta_mediane_instr_per_test[test], 
        )
        d_variation_perc_instr_per_test[test] = compute_and_format_perc(
            mediane([d['instructions'] for d in data_per_test_v1[test]]),
            mediane_delta_instr_per_test[test], 
        )
        delta_mediane_durations_per_test[test] = mediane_delta(
            [d['duration|ns'] for d in data_per_test_v1[test]],
            [d['duration|ns'] for d in data_per_test_v2[test]]
        )
        mediane_delta_durations_per_test[test] = mediane_of_delta(
            [d['duration|ns'] for d in data_per_test_v1[test]],
            [d['duration|ns'] for d in data_per_test_v2[test]]
        )
        variation_perc_durations_per_test[test] = compute_and_format_perc(
            mediane([d['duration|ns'] for d in data_per_test_v1[test]]),
            delta_mediane_durations_per_test[test], 
        )
        d_variation_perc_durations_per_test[test] = compute_and_format_perc(
            mediane([d['duration|ns'] for d in data_per_test_v1[test]]),
            mediane_delta_durations_per_test[test], 
        )

    write_json(output_demo_directory_v1 + 'mediane.json', mediane_per_test_per_measures_v1)
    write_json(output_demo_directory_v1 + 'stddev.json', stddev_per_test_per_measures_v1)
    write_json(output_demo_directory_v1 + 'cv.json', cv_per_test_per_measures_v1)
    write_json(output_demo_directory_v1 + 'qcd.json', qcd_per_test_per_measures_v1)
    write_json(output_demo_directory_v2 + 'mediane.json', mediane_per_test_per_measures_v2)
    write_json(output_demo_directory_v2 + 'stddev.json', stddev_per_test_per_measures_v2)
    write_json(output_demo_directory_v2 + 'cv.json', cv_per_test_per_measures_v2)
    write_json(output_demo_directory_v2 + 'qcd.json', qcd_per_test_per_measures_v2)
    
    mediane_energy_p, mediane_energy_n = split_data_array(dict_to_array(delta_mediane_energy_per_test))
    mediane_instructions_p, mediane_instructions_n = split_data_array(dict_to_array(delta_mediane_instr_per_test))
    mediane_durations_p, mediane_durations_n = split_data_array(dict_to_array(delta_mediane_durations_per_test))

    mediane_d_energy_p, mediane_d_energy_n = split_data_array(dict_to_array(mediane_delta_energy_per_test))
    mediane_d_instructions_p, mediane_d_instructions_n = split_data_array(dict_to_array(mediane_delta_instr_per_test))
    mediane_d_durations_p, mediane_d_durations_n = split_data_array(dict_to_array(mediane_delta_durations_per_test))

    variations_energy = dict_to_array(variation_perc_energy_per_test)
    variations_instr = dict_to_array(variation_perc_instr_per_test)
    variations_durations = dict_to_array(variation_perc_durations_per_test)
    
    d_variations_energy = dict_to_array(d_variation_perc_energy_per_test)
    d_variations_instr = dict_to_array(d_variation_perc_instr_per_test)
    d_variations_durations = dict_to_array(d_variation_perc_durations_per_test)

    print(mediane_energy_p, mediane_energy_n)
    print(mediane_instructions_p, mediane_instructions_n)
    print(mediane_durations_p, mediane_durations_n)

    print(mediane_d_energy_p, mediane_d_energy_n)
    print(mediane_d_instructions_p, mediane_d_instructions_n)
    print(mediane_d_durations_p, mediane_d_durations_n)


    test_key = [test.split('-')[-1].split('.')[0] for test in delta_mediane_energy_per_test]

    df = pd.DataFrame(
        {
            'Test': test_key + test_key + test_key,
            'Value_n': mediane_energy_n + mediane_instructions_n + mediane_durations_n,
            'Value_p': mediane_energy_p + mediane_instructions_p + mediane_durations_p,
            'Variation': variations_energy + variations_instr + variations_durations,
            'Value_d_n': mediane_d_energy_n + mediane_d_instructions_n + mediane_d_durations_n,
            'Value_d_p': mediane_d_energy_p + mediane_d_instructions_p + mediane_d_durations_p,
            'Variation_d': d_variations_energy + d_variations_instr + d_variations_durations,
            'Measure': ['Energy' for i in range(len(test_key))] +
            ['Instructions' for i in range(len(test_key))] +
            ['Durations' for i in range(len(test_key))]
        }, 
    )
    print(df)

    plot_delta_as_hist2(
        mediane_energy_p + mediane_instructions_p + mediane_durations_p,
        mediane_energy_n + mediane_instructions_n + mediane_durations_n,
        test_key + test_key + test_key,
        ['Energy' for i in range(len(test_key))] +
        ['Instructions' for i in range(len(test_key))] +
        ['Durations' for i in range(len(test_key))]
    )