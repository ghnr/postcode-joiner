import numpy as np
from pandas import read_csv

# Expected results to assert that output results are equal to this
# Relative path of results needed for pytest call
result_export = read_csv("./results/result.tsv")

haversine_result = np.array([[5.05608563]])
euclidean_result = np.array([[0.04800872]])
coords_result = (np.array([[5.16155e+01, 3.26590e-02],
                           [5.15717e+01, 5.23160e-02],
                           [np.nan, 5.16064e+01],
                           [5.15958e+01, 7.46970e-02],
                           [5.15836e+01, 4.74080e-02],
                           [5.15855e+01, 1.19799e-01],
                           [5.15783e+01, 7.10310e-02],
                           [5.15818e+01, 1.18457e-01],
                           [5.16159e+01, 2.63610e-02],
                           [5.15519e+01, 8.94590e-02]], dtype=np.float32),
                 np.array([[5.1583694e+01, 2.4807423e-02],
                           [5.1584816e+01, 2.5362000e-02],
                           [5.1582348e+01, 2.1159999e-02],
                           [5.1583965e+01, 2.2767000e-02],
                           [5.1615513e+01, 3.2659344e-02],
                           [5.1584709e+01, 2.3220999e-02],
                           [5.1566261e+01, 1.2560000e-01],
                           [5.1567139e+01, 1.2639099e-01]], dtype=np.float32))

extract_result = ['IG8 0NS', 'IG1 3NG', np.nan, 'IG5 0XP', 'IG4 5PU', 'RM6 5SU', np.nan, np.nan, np.nan, np.nan]

speed_result = ['IG8 0NS', 'E11 1PD', 'E11 1PB', 'IG8 0NS', 'E11 1PD', 'RM8 1YQ', 'E11 1PD', 'RM8 1YQ', 'IG8 0NS', 'RM8 1YG']

accuracy_result = ['IG8 0NS', 'E11 1PB', 'E11 1PB', 'E11 1PD', 'E11 1PD', 'RM8 1YQ', 'E11 1PD', 'RM8 1YQ', 'IG8 0NS', 'RM8 1YG']

valid_result = [True, False, False, False, False, False, False, False, False, False]
