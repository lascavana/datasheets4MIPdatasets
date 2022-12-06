import time
import numpy as np
import pyscipopt as scip

class FourPhaseRec(scip.Eventhdlr):
  """
  A SCIP event handler that records the 3 solving stages:
  feasibility, improvement, proof.
  """
  def __init__(self):
    # record solutions and time #
    self.times = []
    self.start = -1.0
    self.solutions = []

    # record phase lengths #
    self.phase1 = -1.0
    self.phase2 = -1.0
    self.phase3 = -1.0
    self.phase4 = -1.0

  def eventinit(self):
    self.start = time.time()
    self.model.catchEvent(scip.SCIP_EVENTTYPE.BESTSOLFOUND, self)

  def eventexit(self):
    self.model.dropEvent(scip.SCIP_EVENTTYPE.BESTSOLFOUND, self)

    currenttime = time.time()

    # determine solution that marks beginning of phase III #
    solutions = np.array(self.solutions)
    percentage_diff = abs(solutions - solutions[-1]) / (abs(solutions[-1]) + 1e-6)
    k = np.where(percentage_diff < 0.05)[0][0]

    # calculate lenght of each phase #
    self.phase1 = self.times[0] - self.start
    self.phase2 = self.times[k] - self.times[0]
    self.phase3 = self.times[-1] - self.times[k]
    self.phase4 = currenttime - self.times[-1] 

  def eventexec(self, event):
    currenttime = time.time()
    currentsol = self.model.getSolObjVal( self.model.getBestSol() , original=True )

    self.times.append(currenttime)
    self.solutions.append(currentsol)


class PrimalDualTrack(scip.Eventhdlr):
  """
  A SCIP event handler that keeps track of the primal and dual 
  bound improvements.
  """
  def __init__(self):
    # record times #
    self.primal = []
    self.dual = []

  def eventinit(self):
    self.model.catchEvent(scip.SCIP_EVENTTYPE.BESTSOLFOUND, self)
    self.model.catchEvent(scip.SCIP_EVENTTYPE.NODESOLVED, self)

  def eventexit(self):
    self.model.dropEvent(scip.SCIP_EVENTTYPE.BESTSOLFOUND, self)
    self.model.dropEvent(scip.SCIP_EVENTTYPE.NODESOLVED, self)

  def eventexec(self, event):
    primalboud = self.model.getPrimalbound()
    dualbound = self.model.getDualbound()

    self.primal.append(primalboud)
    self.dual.append(dualbound)


class FirstBranchTime(scip.Eventhdlr):
  """
  A SCIP event handler that records when the first
  branching happens.
  """
  def __init__(self):
    self.start = -1.0
    self.elapsed = -1.0

  def eventinit(self):
    self.start = time.time()
    self.model.catchEvent(scip.SCIP_EVENTTYPE.NODEBRANCHED, self)

  def eventexec(self, event):
    self.elapsed = time.time() - self.start
    self.model.dropEvent(scip.SCIP_EVENTTYPE.NODEBRANCHED, self)

# class EventHandler(scip.Eventhdlr):
#   """
#   A SCIP event handler that records solving stats
#   """
#   def __init__(self):
#     self.first_call = True

#     self.lastbound = None
#     self.lasttime = None
#     self.invert = False
#     self.integral = 0.0

#     self.degeneracy = 0.0
#     self.varconsratio = 1.0

#   def eventinit(self):
#     self.model.catchEvent(scip.SCIP_EVENTTYPE.NODESOLVED, self)

#   def eventexit(self):
#     self.model.dropEvent(scip.SCIP_EVENTTYPE.NODESOLVED, self)

#   def eventexec(self, event):
#     # event_type = event.getType()

#     if self.first_call:
#       self.first_call = False

#       # save time / bound info #
#       self.lasttime = self.model.getSolvingTime()
#       self.lastbound = self.model.getLowerbound()
#       if self.lastbound < 0.0: self.invert = True

#       # save degeneracy data #
#       degeneracy, varconsratio = self.model.getLPDualDegeneracy()
#       self.degeneracy = degeneracy
#       self.varconsratio = varconsratio

#       return


#     time = self.model.getSolvingTime()
#     bound = self.model.getLowerbound()
#     if abs(bound - self.lastbound) < 1e-6: return

#     print("here")

#     # update integral #
#     if self.invert: # record integral of 1/d(t)
#       if bound >= 1e-6: # crossed the origin. Switch to d(t).
#         self.integral = 0.0
#         self.invert = False
#       else:
#         self.integral += (1/(bound+1e-6) - 1/(self.lastbound+1e-6)) * (time - self.lasttime)/2
#     else: # record integral of d(t)
#       self.integral += (bound - self.lastbound) * (time - self.lasttime)/2;
    
#     # save values #
#     self.lasttime = time
#     self.lastbound = bound

#   def dualint(self):
#     # no branching took place #
#     if self.first_call: 
#       return 0.0

#     optimal = self.model.getObjVal()
#     time = self.model.getSolvingTime()

#     if not self.invert:
#       self.integral += (time-self.lasttime) * (optimal - self.lastbound)/2
#       self.integral /= optimal
#       self.integral = time/2 - self.integral
#     else:
#       self.integral += (time-self.lasttime) * (1/(optimal+1e-6) - 1/(self.lastbound+1e-6))/2
#       self.integral *= optimal
#       self.integral = time/2 - self.integral
    
#     return self.integral




