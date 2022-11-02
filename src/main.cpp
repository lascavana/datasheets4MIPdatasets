#include <chrono>
#include <iostream>
#include <fstream>

// SCIP
#include "objscip/objscip.h"
#include "objscip/objconshdlr.h"
#include "objscip/objscipdefplugins.h"

#include "EventhdlrProbe.hpp"

using namespace scip;
using namespace std;

class Logger
{
  public:
  string filename;

  Logger(string name)
  {
    filename = name;
  }

  void log(string line)
  {
    ofstream logfile;
    logfile.open(filename, ofstream::app);
    logfile << line << "\n";
    logfile.close();
  }
};


/** reads parameters */
static
SCIP_RETCODE readParams(
   SCIP*                      scip,               /**< SCIP data structure */
   const char*                filename            /**< parameter file name, or NULL */
   )
{
   if( filename != NULL )
   {
      if( SCIPfileExists(filename) )
      {
         cout << "reading parameter file <" << filename << ">" << endl;
         SCIP_CALL( SCIPreadParams(scip, filename) );
      }
      else
         cout << "parameter file <" << filename << "> not found - using default parameters" << endl;
   }
   else if( SCIPfileExists("scipmip.set") )
   {
      cout << "reading parameter file <scipmip.set>" << endl;
      SCIP_CALL( SCIPreadParams(scip, "scipmip.set") );
   }

   return SCIP_OKAY;
}

/** starts SCIP */
static
SCIP_RETCODE fromCommandLine(
   SCIP*                      scip,               /**< SCIP data structure */
   const char*                filename            /**< input file name */
   )
{
   /********************
    * Problem Creation *
    ********************/

   cout << endl << "read problem <" << filename << ">" << endl;
   cout << "============" << endl << endl;
   SCIP_CALL( SCIPreadProb(scip, filename, NULL) );

   /*******************
    *    Pre-solve    *
    *******************/
   SCIP_CALL( SCIPpresolve(scip) );
   int m = SCIPgetNConss(scip);
   int n = SCIPgetNVars(scip);
   cout << "Number of constraints: " << m << "\n";
   cout << "Number of variables: " << n << "\n";


   /*******************
    * Problem Solving *
    *******************/

   /* solve problem */
   cout << "solve problem" << endl;
   cout << "=============" << endl;
   SCIP_CALL( SCIPsolve(scip) );
   cout << endl << "FINISHED" << endl;
   cout << "================" << endl << endl;


   /**************
    * Statistics *
    **************/

   // cout << endl << "Statistics" << endl;
   // cout << "==========" << endl << endl;
   //
   // SCIP_CALL( SCIPprintStatistics(scip, NULL) );

   return SCIP_OKAY;
}


/** creates a SCIP instance with default plugins, evaluates command line parameters, runs SCIP appropriately,
 *  and frees the SCIP instance
 */
static
SCIP_RETCODE runSCIP(
   int                        argc,               /**< number of shell parameters */
   char**                     argv                /**< array with shell parameters */
   )
{
   SCIP* scip = NULL;

   /*********
    * Setup *
    *********/

   /* initialize SCIP */
   SCIP_CALL( SCIPcreate(&scip) );

   /***********************
    * Version information *
    ***********************/

   SCIPprintVersion(scip, NULL);
   cout << endl;

   EventhdlrProbe Eventhdlr(scip, argv[1]);
   SCIP_CALL( SCIPincludeObjEventhdlr(scip, &Eventhdlr, FALSE) );

   /* include default SCIP plugins */
   SCIP_CALL( SCIPincludeDefaultPlugins(scip) );


   /**************
    * Parameters *
    **************/

   if( argc >= 3 )
   {
      SCIP_CALL( readParams(scip, argv[2]) );
   }
   else
   {
      SCIP_CALL( readParams(scip, NULL) );
   }
   /*CHECK_OKAY( SCIPwriteParams(scip, "scipmip.set", TRUE) );*/


   /**************
    * Start SCIP *
    **************/

   SCIP_CALL( fromCommandLine(scip, argv[1]) );

   /**************
    * Log stats *
    **************/
    ofstream logfile;
    logfile.open("log.txt", ofstream::app);
    logfile << "[INSTANCE] " << argv[1] << endl;
    // logfile << "[SEED] " << "??" << endl;
    logfile << "[ROOTDEGENERACY] " << Eventhdlr.eventhdlrdata.degeneracy << endl;
    logfile << "[ROOTVARCONSRATIO] " << Eventhdlr.eventhdlrdata.varconsratio << endl;
    logfile << "[FIRSTLPTIME] " << SCIPgetFirstLPTime(scip) << endl;
    logfile << "[ROOTTIME] " << Eventhdlr.eventhdlrdata.roottime << endl;
    logfile.close();


   /********************
    * Deinitialization *
    ********************/

   SCIP_CALL( SCIPfree(&scip) );

   BMScheckEmptyMemory();

   return SCIP_OKAY;
}


/** main method starting SCIP */
int main(
   int                        argc,          /**< number of arguments from the shell */
   char**                     argv           /**< array of shell arguments */
   )
{
   /* print usage */
   cout << " usage: project9 filename settingsfile" << endl;

   /* check usage */
   if( argc < 2 )
   {
     cout << " No file provided. Please enter a filename. " << endl;
     return 1;
   }

   /* run SCIP */
   SCIP_RETCODE retcode;
   retcode = runSCIP(argc, argv);
   if( retcode != SCIP_OKAY )
   {
      SCIPprintError(retcode);
      return -1;
   }

   return 0;
}
