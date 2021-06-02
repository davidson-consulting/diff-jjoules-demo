import os
import sys
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def read_json(path_to_json):
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    return data

def plot_delta_as_hist2(data_p, data_n, labels, unit, output):
    df = pd.DataFrame(
        {
            'Test': labels,
            'Value_n': data_n,
            'Value_p': data_p,
        }, 
    )
    print(df)
    bar_plot = sns.barplot(x="Test", y='Value_p', data=df)
    bar_plot = sns.barplot(x="Test", y='Value_n', data=df)

    bar_plot.set_ylabel(unit)
    #plt.savefig('target/demo-output/graph_' + output)
    #plt.clf()

def run_cmd(cmd):
    print(cmd)
    os.system(cmd)

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

def dict_to_array(data):
    return [data[key] for key in data]

ITERATION = 3

tests = [ 
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapEmptyList.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapOneElement.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapMultipleElement.json'
]

if __name__ == '__main__':

    output_folder = 'target/demo-output/'

    data_per_test_v1 = {}
    data_per_test_v2 = {}

    for test in tests:
        data_per_test_v1[test] = []
        data_per_test_v2[test] = []
        for i in range(1, ITERATION + 1):
            data_per_test_v1[test].append(read_json(output_folder + 'v1/' + str(i) + '/' + test))
            data_per_test_v2[test].append(read_json(output_folder + 'v2/' + str(i) + '/' + test))
    
    delta_mediane_energy_per_test = {}
    delta_mediane_instr_per_test = {}
    for test in tests:
        delta_mediane_energy_per_test[test] = mediane_delta(
            [d['package|uJ'] for d in data_per_test_v1[test]],
            [d['package|uJ'] for d in data_per_test_v2[test]]
        )
        delta_mediane_instr_per_test[test] = mediane_delta(
            [d['instructions'] for d in data_per_test_v1[test]],
            [d['instructions'] for d in data_per_test_v2[test]]
        )
        
    mediane_energy_p, mediane_energy_n = split_data_array(dict_to_array(delta_mediane_energy_per_test))
    mediane_instr_p, mediane_instr_n = split_data_array(dict_to_array(delta_mediane_instr_per_test))

    test_key = [test.split('-')[-1].split('.')[0] for test in delta_mediane_energy_per_test]
    plot_delta_as_hist2(
        mediane_energy_p,
        mediane_energy_n,
        test_key,
        'Energy(uJ)',
        'energy.png'
    )
    plt.figure()
    plot_delta_as_hist2(
        mediane_instr_p,
        mediane_instr_n,
        test_key,
        '# Instructions',
        'instr.png'
    )

    plt.show()