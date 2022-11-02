#include <cmath>
#include <string>
#include <vector>
#include <cassert>
#include <fstream>
#include <iostream>
#include <unordered_map>

// SCIP
#include <scip/scip.h>
#include <scip/scipdefplugins.h>

#include "EventhdlrProbe.hpp"

/** destructor of event handler to free user data (called when SCIP is exiting) */
SCIP_DECL_EVENTFREE(EventhdlrProbe::scip_free)
{  /*lint --e{715}*/
   return SCIP_OKAY;
}


/** initialization method of event handler (called after problem was transformed) */

SCIP_DECL_EVENTINIT(EventhdlrProbe::scip_init)
{  /*lint --e{715}*/
   return SCIP_OKAY;
}


/** deinitialization method of event handler (called before transformed problem is freed) */

SCIP_DECL_EVENTEXIT(EventhdlrProbe::scip_exit)
{  /*lint --e{715}*/
   return SCIP_OKAY;
}


/** solving process initialization method of event handler (called when branch and bound process is about to begin)
 *
 *  This method is called when the presolving was finished and the branch and bound process is about to begin.
 *  The event handler may use this call to initialize its branch and bound specific data.
 *
 */

SCIP_DECL_EVENTINITSOL(EventhdlrProbe::scip_initsol)
{
   SCIP_CALL( SCIPcatchEvent( scip, SCIP_EVENTTYPE_NODESOLVED, eventhdlr, NULL, NULL) );

   return SCIP_OKAY;
}


/** solving process deinitialization method of event handler (called before branch and bound process data is freed)
 *
 *  This method is called before the branch and bound process is freed.
 *  The event handler should use this call to clean up its branch and bound data.
 */

SCIP_DECL_EVENTEXITSOL(EventhdlrProbe::scip_exitsol)
{
   SCIP_CALL( SCIPdropEvent( scip, SCIP_EVENTTYPE_NODESOLVED, eventhdlr, NULL, -1) );
   return SCIP_OKAY;
}


/** frees specific constraint data */

SCIP_DECL_EVENTDELETE(EventhdlrProbe::scip_delete)
{  /*lint --e{715}*/
   return SCIP_OKAY;
}


/** execution method of event handler
 *
 *  Processes the event. The method is called every time an event occurs, for which the event handler
 *  is responsible. Event handlers may declare themselves resposible for events by calling the
 *  corresponding SCIPcatch...() method. This method creates an event filter object to point to the
 *  given event handler and event data.
 */
SCIP_DECL_EVENTEXEC(EventhdlrProbe::scip_exec)
{  /*lint --e{715}*/

  eventhdlrdata.callcounter++;

  /* root node */
  if (eventhdlrdata.callcounter == 1)
  {
    eventhdlrdata.lastbound = SCIPgetLowerbound(scip);
    eventhdlrdata.lasttime = SCIPgetSolvingTime(scip);

    if( eventhdlrdata.lastbound < 0.0) eventhdlrdata.invert = true;

    /* get dual degeneracy metrics */
    SCIP_Real degeneracy, varconsratio;
    SCIPgetLPDualDegeneracy(scip, &degeneracy, &varconsratio);
    eventhdlrdata.degeneracy = degeneracy;
    eventhdlrdata.varconsratio = varconsratio;

    /* time to solve root node */
    eventhdlrdata.roottime = SCIPgetSolvingTime(scip);

    SCIP_CALL( SCIPinterruptSolve(scip) );

    return SCIP_OKAY;
  }

  /* get current time and bound */
  SCIP_Real currbound = SCIPgetLowerbound(scip);
  SCIP_Real currtime = SCIPgetSolvingTime(scip);

  /* dual integral */
  if (abs(currbound - eventhdlrdata.lastbound) < 1e-6)
  {
    return SCIP_OKAY;
  }
  else
  {
    if (eventhdlrdata.invert) // record integral of 1/d(t)
    {
      if (currbound >= 1e-6) // crossed the origin. Switch to d(t).
      {
        eventhdlrdata.dualint = 0.0;
        eventhdlrdata.invert = false;
      }
      else
      {
        eventhdlrdata.dualint += (1/(currbound+1e-6) - 1/(eventhdlrdata.lastbound+1e-6)) * (currtime - eventhdlrdata.lasttime)/2;
      }
    }
    else // record integral of d(t)
    {
      eventhdlrdata.dualint += (currbound - eventhdlrdata.lastbound) * (currtime - eventhdlrdata.lasttime)/2;
    }

    eventhdlrdata.lastbound = currbound;
    eventhdlrdata.lasttime = currtime;
  }
  
  return SCIP_OKAY;
}


double EventhdlrProbe::calculate_dualintegral(
  SCIP* scip
)
{
  if (eventhdlrdata.callcounter == 0) return 0.0; // no branching took place


  SCIP_SOL* bestsol = SCIPgetBestSol(scip);
  SCIP_Real optimal = SCIPgetSolTransObj(scip, bestsol);
  SCIP_Real time = SCIPgetSolvingTime(scip);

  if (not eventhdlrdata.invert)
  {
    eventhdlrdata.dualint += (optimal - eventhdlrdata.lastbound) * (time - eventhdlrdata.lasttime) / 2;
    eventhdlrdata.dualint /= optimal;
    eventhdlrdata.dualint = time/2 - eventhdlrdata.dualint;
  }   
  else
  {
    eventhdlrdata.dualint += (time-eventhdlrdata.lasttime) * (1/(optimal+1e-6) - 1/(eventhdlrdata.lastbound+1e-6));
    eventhdlrdata.dualint *= optimal;
    eventhdlrdata.dualint = time/2 - eventhdlrdata.dualint;
  }  

  return eventhdlrdata.dualint;
}