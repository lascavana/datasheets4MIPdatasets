import csv
import glob
import scipy
import pyscipopt
import numpy as np


problem = 'cauctions'
result_file = f'results/{problem}.csv'
instance_path = f'benchmarks/{problem}'
instances = glob.glob(f"{instance_path}/*.lp")

fieldnames = ['instance', 'seed', 'fingerprint', 'setting', 'nnodes', 'time', 'status', 'gap']

default_settings = {'limits/time': 3600,
                    'limits/memory': 4000,
                    'timing/clocktype': 1,
                    'display/verblevel': 0,
                    'randomization/permutevars': True,
                    'separating/maxroundsroot': -1,
                    'separating/maxrounds': -1,
                    'branching/relpscost/priority': 10000,
                    'branching/random/priority': -100000,
                    'branching/vanillafullstrong/priority': -2000
                    }

additional_settings = {'default': {},
                       'nocutting': {'separating/maxroundsroot': 0, 'separating/maxrounds': 0},
                       'randombranch': {'branching/relpscost/priority': 99999},
                       'vfsbranch': {'branching/vanillafullstrong/priority': 99999}
                      }


# create model #
m = pyscipopt.Model()

# solve instances #
with open(result_file, 'w', newline='') as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
  writer.writeheader()

  for instance in instances:
    for sett in additional_settings:
      for seed in range(3):
        print(f"~~ Instance {instance}, seed {seed}, settings {sett}")

        fingerprint = instance.split('_')[2] + instance.split('_')[3][:-3]

        results = {'instance': instance,
                  'fingerprint': fingerprint,
                  'setting': sett,
                  'seed': seed }


        m.readProblem(instance)
        m.setParam('randomization/permutationseed', seed)
        m.setParam('randomization/randomseedshift', seed)
        m.setParams(default_settings)
        m.setParams(additional_settings[sett])

        m.optimize()

        print("... solved")
        results['nnodes'] = m.getNTotalNodes()
        results['time'] = m.getSolvingTime()
        results['status'] = m.getStatus()
        results['gap'] = m.getGap()
        print(results)

        m.freeProb()

        writer.writerow(results)
        csvfile.flush()


