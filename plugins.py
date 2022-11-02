import pyscipopt as scip

class EventHandler(scip.Eventhdlr):
  """
  A SCIP event handler that records solving stats
  """
  def __init__(self):
    self.first_call = True

    self.lastbound = None
    self.lasttime = None
    self.invert = False
    self.integral = 0.0

    self.degeneracy = 0.0
    self.varconsratio = 1.0

  def eventinit(self):
    self.model.catchEvent(scip.SCIP_EVENTTYPE.NODESOLVED, self)

  def eventexit(self):
    self.model.dropEvent(scip.SCIP_EVENTTYPE.NODESOLVED, self)

  def eventexec(self, event):
    # event_type = event.getType()

    if self.first_call:
      self.first_call = False

      # save time / bound info #
      self.lasttime = self.model.getSolvingTime()
      self.lastbound = self.model.getLowerbound()
      if self.lastbound < 0.0: self.invert = True

      # save degeneracy data #
      degeneracy, varconsratio = self.model.getLPDualDegeneracy()
      self.degeneracy = degeneracy
      self.varconsratio = varconsratio

      return


    time = self.model.getSolvingTime()
    bound = self.model.getLowerbound()
    if abs(bound - self.lastbound) < 1e-6: return

    print("here")

    # update integral #
    if self.invert: # record integral of 1/d(t)
      if bound >= 1e-6: # crossed the origin. Switch to d(t).
        self.integral = 0.0
        self.invert = False
      else:
        self.integral += (1/(bound+1e-6) - 1/(self.lastbound+1e-6)) * (time - self.lasttime)/2
    else: # record integral of d(t)
      self.integral += (bound - self.lastbound) * (time - self.lasttime)/2;
    
    # save values #
    self.lasttime = time
    self.lastbound = bound

  def dualint(self):
    # no branching took place #
    if self.first_call: 
      return 0.0

    optimal = self.model.getObjVal()
    time = self.model.getSolvingTime()

    if not self.invert:
      self.integral += (time-self.lasttime) * (optimal - self.lastbound)/2
      self.integral /= optimal
      self.integral = time/2 - self.integral
    else:
      self.integral += (time-self.lasttime) * (1/(optimal+1e-6) - 1/(self.lastbound+1e-6))/2
      self.integral *= optimal
      self.integral = time/2 - self.integral
    
    return self.integral




