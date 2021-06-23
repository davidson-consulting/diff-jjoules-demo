import os
import csv
import json
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from shutil import rmtree

def delete_directory(directory):
    if os.path.isdir(directory):
        rmtree(directory)

def get_tests_to_execute(path):
    tests_to_execute = {}
    with open(path, 'r') as csvfile:
        file = csv.reader(csvfile, delimiter=';')
        for line in file:
            tests_to_execute[line[0]] = line[1:]
    return tests_to_execute

def read_json(path_to_json):
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    return data

def mediane_delta(data_v1, data_v2):
    return mediane(data_v2) - mediane(data_v1)

def mediane(data):
    data = sorted(data)
    if len(data) % 2 == 0:
        middle_cursor = int(len(data) / 2)
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

def plot_delta_as_hist(data, labels, unit, output='graph.png', show=False):
    data_p, data_n = [], []
    for d in data:
        if d > 0:
            data_p.append(d)
            data_n.append(0)
        else:
            data_n.append(d)
            data_p.append(0)
    classifier_p = unit + '_p'
    classifier_n = unit + '_n'
    df = pd.DataFrame(
                {
                    'Test': labels,
                    classifier_p: data_p,
                    classifier_n: data_n,
                }, 
                index=labels)
    bar_plot = sns.barplot(x="Test", y=classifier_p, data=df, order=labels, color='red')
    bar_plot = sns.barplot(x='Test', y=classifier_n, data=df, order=labels, color='blue')
    bar_plot.set(ylabel=unit, xlabel="Test")
    plt.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig(output + '.png')
    plt.clf()

def plot_delta_as_hist2(data_p, data_n, labels, units):
    print(len(data_p), len(data_n), len(labels), len(units))
    print(data_p)
    print(data_n)
    print(labels)
    print(units)
    df = pd.DataFrame(
        {
            'Test': labels,
            'Value_n': data_n,
            'Value_p': data_p,
            'Measure': units
        }, 
    )
    print(df)
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

SHA_V1 = '4b8e6f61785365106ccef935cb871b31026bcab8'
SHA_V2 = 'fab0472332025d2c8cc6dc1dd2a11d10d3015352'

target_jjoules_reports_folder = 'target/jjoules-reports/'

tests = [ 
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapEmptyList.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapOneElement.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapMultipleElement.json'
]

warmup_test_name = 'aaaaa_warmup'

output_demo_directory = 'target/demo-ouput/'
output_demo_directory_v1 = output_demo_directory + 'v1/'
output_demo_directory_v2 = output_demo_directory + 'v2/'

if __name__ == '__main__':

    prefix_folder_target = 'target/demo-output'

    data_per_test_v1 = {}
    data_per_test_v2 = {}

    for test in tests:
        data_per_test_v1[test] = []
        data_per_test_v2[test] = []
        for i in range(0, 5):
            data_per_test_v1[test].append(read_json(prefix_folder_target + '/v1/' + str(i) + '/' + test))
            data_per_test_v2[test].append(read_json(prefix_folder_target + '/v2/' + str(i) + '/' + test))

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
        delta_mediane_instr_per_test[test] = mediane_delta(
            [d['instructions'] for d in data_per_test_v1[test]],
            [d['instructions'] for d in data_per_test_v2[test]]
        )
        delta_mediane_durations_per_test[test] = mediane_delta(
            [d['duration|ns'] for d in data_per_test_v1[test]],
            [d['duration|ns'] for d in data_per_test_v2[test]]
        )
    
        plt.plot([d['package|uJ'] for d in data_per_test_v1[test]])
        plt.plot([d['package|uJ'] for d in data_per_test_v2[test]])
        mediane_v1 = mediane([d['package|uJ'] for d in data_per_test_v1[test]])
        mediane_v2 = mediane([d['package|uJ'] for d in data_per_test_v2[test]])
        plt.plot([mediane_v1 for x in range(len(data_per_test_v1[test]))])
        plt.plot([mediane_v2 for x in range(len(data_per_test_v1[test]))])
        plt.savefig(prefix_folder_target + '/' + test + 'energy.png')
        plt.clf()
        plt.plot([d['instructions'] for d in data_per_test_v1[test]])
        plt.plot([d['instructions'] for d in data_per_test_v2[test]])
        mediane_v1 = mediane([d['instructions'] for d in data_per_test_v1[test]])
        mediane_v2 = mediane([d['instructions'] for d in data_per_test_v2[test]])
        plt.plot([mediane_v1 for x in range(len(data_per_test_v1[test]))])
        plt.plot([mediane_v2 for x in range(len(data_per_test_v1[test]))])
        plt.savefig(prefix_folder_target + '/' + test + 'instructions.png')
        plt.clf()
    
    mediane_energy_p, mediane_energy_n = split_data_array(dict_to_array(delta_mediane_energy_per_test))
    mediane_instructions_p, mediane_instructions_n = split_data_array(dict_to_array(delta_mediane_instr_per_test))
    mediane_durations_p, mediane_durations_n = split_data_array(dict_to_array(delta_mediane_durations_per_test))

    print(mediane_energy_p, mediane_energy_n)
    print(mediane_instructions_p, mediane_instructions_n)
    print(mediane_durations_p, mediane_durations_n)
    
    test_key = [to_readable_test_name(test) for test in delta_mediane_energy_per_test]

    plot_delta_as_hist2(
        mediane_energy_p + mediane_instructions_p + mediane_durations_p,
        mediane_energy_n + mediane_instructions_n + mediane_durations_n,
        test_key + test_key + test_key,
        ['Energy' for i in range(len(test_key))] +
        ['Instructions' for i in range(len(test_key))] +
        ['Durations' for i in range(len(test_key))]
    )