import csv
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def gmean(x):
  x = np.array(x)
  if np.where(x==0.0)[0].size > 0:
    return 0.0
  else:
    a = np.log(x)
    return np.exp(a.mean())


result_file = "results/cauctions_100500.csv"

# read csv file #
results = {}
data = pd.read_csv(result_file)
instances = set(data['instance'])
seeds = set(data['seed'])
settings = set(data['setting'])

# read results according to metric of choice #
metric = 'nnodes'
results = {setting: [] for setting in settings}
for setting in settings:
  d = data.loc[data['setting'] == setting]
  for instance in instances:
    i_data = d.loc[data['instance'] == instance]
    vals = []
    for seed in seeds:
      is_data = i_data.loc[i_data['seed'] == seed]
      vals.append(is_data[metric].values[0])

    vals = gmean(vals)
    results[setting].append(vals)

means = []
stds = []
for setting in settings:
  mean = gmean(results[setting])
  means.append(mean)
  stds.append(np.std(results[setting]))
  print(f"{setting}: {mean:.2f} \pm {stds[-1]:.2f}")


