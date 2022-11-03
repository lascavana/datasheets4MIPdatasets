import numpy as np 

with open('results/nn_verification.txt') as f:
  lines = f.readlines()

nvars = []
nconss = []
roottime = []
nvarsorig = []
nconssorig = []
degeneracy = []
varconsratio = []

nint = []
nbin = []
ncont = []

for line in lines:
  line = line.split(' ')

  if line[0] == "[NVARSORIG]":
    nvarsorig.append( int(line[1][:-1]) )

  if line[0] == "[NCONSSSORIG]":
    nconssorig.append( int(line[1][:-1]) )

  if line[0] == "[NVARS]":
    nvars.append( int(line[1][:-1]) )

  if line[0] == "[NCONSS]":
    nconss.append( int(line[1][:-1]) )

  if line[0] == "[NBINVARS]":
    nbin.append( int(line[1][:-1]) )

  if line[0] == "[NCONTVARS]":
    ncont.append( int(line[1][:-1]) )

  if line[0] == "[NINTVARS]":
    nint.append( int(line[1][:-1]) )

  if line[0] == "[ROOTDEGENERACY]":
    degeneracy.append( float(line[1][:-1]) )

  if line[0] == "[ROOTVARCONSRATIO]":
    varconsratio.append( float(line[1][:-1]) )

  if line[0] == "[ROOTTIME]":
    roottime.append( float(line[1][:-1]) )


prop = np.vstack((nbin,nint,ncont))
prop = prop / np.sum(prop, axis=0)
prop = np.mean(prop, axis=1)


print(f"Median number of original variables  & {np.median(nvarsorig)} \\"+"\\")
print(f"Minimum number of original variables  & {np.amin(nvarsorig)} \\"+"\\")
print(f"Maximum number of original variables  & {np.amax(nvarsorig)} \\"+"\\ \hline")
print(f"Median number of original constraints  & {np.median(nconssorig)} \\"+"\\")
print(f"Minimum number of original constraints  & {np.amin(nconssorig)} \\"+"\\")
print(f"Maximum number of original constraints  & {np.amax(nconssorig)} \\"+"\\ \hline")
print(f"Median number of variables  & {np.median(nvars)} \\"+"\\")
print(f"Minimum number of variables  & {np.amin(nvars)} \\"+"\\")
print(f"Maximum number of variables  & {np.amax(nvars)} \\"+"\\ \hline")
print(f"Median number of constraints  & {np.median(nconss)} \\"+"\\")
print(f"Minimum number of constraints  & {np.amin(nconss)} \\"+"\\")
print(f"Maximum number of constraints  & {np.amax(nconss)} \\"+"\\ \hline")
print(f"Average root degeneracy  & {np.mean(degeneracy):.2f} \\"+"\\")
print(f"Average root var/cons ratio  & {np.mean(varconsratio):.2f} \\"+"\\ \hline")
print(f"Average time to solve root node  & {np.mean(roottime):.2f}s \\"+"\\")
print(f"Average proportion of variable types  & {prop[0]:.2f}(B)/{prop[1]:.2f}(I)/{prop[2]:.2f}(C) \\"+"\\")


