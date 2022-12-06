import csv
import glob
import pyscipopt
import numpy as np

from plugins import FourPhaseRec, FirstBranchTime

problem = 'cauctions'
result_file = f'results/{problem}.csv'
instance_path = f'benchmarks/{problem}'
instances = glob.glob(f"{instance_path}/*.lp")

fieldnames = ['instance', 'seed', 'fingerprint', 'setting', 'nnodes', 'time', 
              'status', 'gap', 'phase1', 'phase2', 'phase3', 'phase4', 'first2opt_ratio',
              'firstbranchtime']

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

        # create model #
        m = pyscipopt.Model()
        m.readProblem(instance)

        # set parameters #
        m.setParam('randomization/permutationseed', seed)
        m.setParam('randomization/randomseedshift', seed)
        m.setParams(default_settings)
        m.setParams(additional_settings[sett])
        
        eveh1 = FourPhaseRec()
        eveh2 = FirstBranchTime()
        m.includeEventhdlr(eveh1, "ThreePhaseRec", "collects info about 3 phases of solving")
        m.includeEventhdlr(eveh2, "FirstBranchTime", "records the time of the first branching")

        m.optimize()

        print("... solved")
        results['nnodes'] = m.getNTotalNodes()
        results['time'] = m.getSolvingTime()
        results['status'] = m.getStatus()
        results['gap'] = m.getGap()
        first2opt_ratio = abs(eveh1.solutions[0] - eveh1.solutions[-1]) / (abs(eveh1.solutions[-1]) + 1e-6)
        results['first2opt_ratio'] = '{:.4f}'.format(first2opt_ratio) 
        results['firstbranchtime'] = '{:.4f}'.format(eveh2.elapsed) 

        m.freeProb()

        results['phase1'] = '{:.4f}'.format(eveh1.phase1) 
        results['phase2'] = '{:.4f}'.format(eveh1.phase2) 
        results['phase3'] = '{:.4f}'.format(eveh1.phase3) 
        results['phase4'] = '{:.4f}'.format(eveh1.phase4) 
        
        print(results)

        writer.writerow(results)
        csvfile.flush()