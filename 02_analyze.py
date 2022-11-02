import csv
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# read csv file #
results = {}
data = pd.read_csv(result_file)
instances = set(data['instance'])
seeds = set(data['seed'])
fingerprints = set(data['fingerprint'])

# read results according to metric of choice #
metric = 'nnodes'
results = {fingerprint: [] for fingerprint in fingerprints}
for instance in instances:
  i_data = data.loc[data['instance'] == instance]
  vals = []
  for seed in seeds:
    is_data = i_data.loc[i_data['seed'] == seed]
    vals.append(is_data[metric].values[0])

  vals = gmean(vals)
  instance_fingerprint = i_data['fingerprint'].values[0]
  results[instance_fingerprint].append(vals)

means = []
stds = []
for fingerprint in ['100500', '2001000', '3001500']:
  print(fingerprint, results[fingerprint])
  mean = gmean(results[fingerprint])
  means.append(mean)
  stds.append(np.std(results[fingerprint]))

plt.errorbar([1,2,3], means, stds)
plt.show()

