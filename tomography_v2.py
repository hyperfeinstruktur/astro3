import numpy as np
import matplotlib.pyplot as plt
import argparse
import pickle as pkl
from common import PoincareCollection, Tomography, PoincareMapper
from potentials import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Poincare x vx Section"
    )

    # Integration Parameters (Collection parameters)
    parser.add_argument("-tf",type=float,default=100,help="Maximal integration time. If --no_count, this will be the obligatory final time")
    parser.add_argument("-N_points",type=int,default= 40,help="Terminate integration after n crossings of the plane (=nb of points in the Poincaré map)")
    parser.add_argument("-N_orbits",type=int,default=11,help="Number of orbits to sample if --fill is passed")

    # Tomography Parameters
    parser.add_argument("-Emin",type=float,default=30.)
    parser.add_argument("-Emax",type=float,default=200.)
    parser.add_argument("-N_E",type=int,default=3,help="Number of energy slices in tomographic mode")
    parser.add_argument("--no_orbit_redraw",action='store_false')

    # Script Parameters
    parser.add_argument("--progress",action='store_true',help="Use tqdm to show progress bar")
    parser.add_argument("-save",type=str,default=None)
    parser.add_argument("-open",type=str,default=None)

    args = parser.parse_args()
    # Define an event function (crossing of the y plane)
    def event_yplanecross(t,y):
        return y[1]
    event_yplanecross.direction = 1

    if args.open is None:
        # Define a potential
        r0 = (0,0)
        logpot = LogarithmicPotential(zeropos=r0)
        rotpot = zRotation(0.3,zeropos=r0)
        pot = CombinedPotential(logpot,rotpot)

        # Mapper with default parameters for integration time etc
        mapper = PoincareMapper(pot,event_yplanecross)

        # Create Poincare sections over a range of energies
        energylist = np.linspace(args.Emin,args.Emax,args.N_E)
        orbitslist = []
        sectionslist = np.empty((args.N_E,args.N_orbits,2,args.N_points))
        zvclist = np.empty((args.N_E,2,800)) # 400 see in PoincareMapper (TODO)
        for j,e in enumerate(energylist):
            s,o,zvc = mapper.section(e,args.N_orbits,args.N_points)
            orbitslist.append(o)
            sectionslist[j] = s
            zvclist[j] = zvc
            
        col = PoincareCollection(energylist,orbitslist,sectionslist,zvclist,mapper)

        if args.save is not None:
            with open(args.save,'wb') as f:
                pkl.dump(col,f)

    else:
        with open(args.open,'rb') as f:
            col = pkl.load(f)
    
        mapper = col.mapper
        orbitslist = col.orbitslist
        sectionslist = col.sectionsarray
        energylist = col.energylist
        zvclist = col.zvc_list
    
    # Tomographic plot
    tom = Tomography(sectionslist,orbitslist,zvclist,energylist,mapper)
    

    plt.show()