#ifndef __EVENTHDLRMATREAD_H__
#define __EVENTHDLRMATREAD_H__

#include "objscip/objscip.h"
#include "objscip/objeventhdlr.h"

struct EventhdlrProbeData
{
  int invert;
  int callcounter;
  SCIP_Real lastbound;
  SCIP_Real lasttime;
  double dualint;
  SCIP_Real degeneracy;
  SCIP_Real varconsratio;
  SCIP_Real roottime;
};


/** C++ wrapper object for event handlers */
class EventhdlrProbe : public scip::ObjEventhdlr
{
public:

   char* instancepath;
   EventhdlrProbeData eventhdlrdata;

   /** default constructor */
   EventhdlrProbe(
      SCIP* scip,
      char* filename
      )
      : ObjEventhdlr(scip, "matread","Read constraint matrix after first LP is solved")
   {
     instancepath = filename;
     eventhdlrdata.callcounter = 0;
     eventhdlrdata.dualint = 0.0;
     eventhdlrdata.invert = false;
   }

   /** destructor */
   virtual ~EventhdlrProbe()
   {}

   /** destructor of event handler to free user data (called when SCIP is exiting) */
   virtual SCIP_DECL_EVENTFREE(scip_free);

   /** initialization method of event handler (called after problem was transformed) */
   virtual SCIP_DECL_EVENTINIT(scip_init);

   /** deinitialization method of event handler (called before transformed problem is freed) */
   virtual SCIP_DECL_EVENTEXIT(scip_exit);

   /** solving process initialization method of event handler (called when branch and bound process is about to begin)
    *
    *  This method is called when the presolving was finished and the branch and bound process is about to begin.
    *  The event handler may use this call to initialize its branch and bound specific data.
    *
    */
   virtual SCIP_DECL_EVENTINITSOL(scip_initsol);

   /** solving process deinitialization method of event handler (called before branch and bound process data is freed)
    *
    *  This method is called before the branch and bound process is freed.
    *  The event handler should use this call to clean up its branch and bound data.
    */
   virtual SCIP_DECL_EVENTEXITSOL(scip_exitsol);

   /** frees specific constraint data */
   virtual SCIP_DECL_EVENTDELETE(scip_delete);

   /** execution method of event handler
    *
    *  Processes the event. The method is called every time an event occurs, for which the event handler
    *  is responsible. Event handlers may declare themselves resposible for events by calling the
    *  corresponding SCIPcatch...() method. This method creates an event filter object to point to the
    *  given event handler and event data.
    */
   virtual SCIP_DECL_EVENTEXEC(scip_exec);

   double calculate_dualintegral(SCIP* scip);
}; /*lint !e1712*/



#endif
