# AC Power Flow Equations
# Author: Íngrid Munné-Collado
# Date: 07/05/2021

# Requirements: Install pyomo, glpk and gurobi. You should apply for an academic license in gurobi
from pyomo.environ import *
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np

# Creating the model
model = AbstractModel()

# Sets
# Defining Sets
model.G = Set() # generators
model.D = Set() # demand
model.N = Set() # buses in the network
model.L = Set() # Lines in the network


# Parameters
model.Pgmax = Param(model.G, model.T)
model.Pdmax = Param(model.D, model.T)
model.znn = Param(model.N, model.N)
model.ynn = Param(model.N, model.N)
model.Spqmax = Param(model.N, model.N) # max apparent power q-p
model.Sqpmax = Param(model.N, model.N) # max apparent power p-q
model.location_generators = Param(model.G, model.N)
model.location_demands = Param(model.D, model.N)
model.Y = Param(model.N, model.N)  # admittance matrix

# Variables
model.Pdi = Var(model.D, within=NonNegativeReals)
model.Pgi = Var(model.G,  within=NonNegativeReals)
model.Pi = Var(model.N,  within=NonNegativeReals)
model.Qdi = Var(model.D,  within=NonNegativeReals)
model.Qgi = Var(model.G,  within=NonNegativeReals)
model.Qi = Var(model.N,  within=NonNegativeReals)
model.Vi = Var(model.N, within= NonNegativeReals)
model.thetai = Var(model.N, within=Reals)
model.thetaik = Var(model.N, model.N, within=Reals)
model.Spq =  Var(model.N, model.N,  within=Reals)
model.Sqp =  Var(model.N, model.N,  within=Reals)


# Objective Function
def OF(model):
    return 1
model.dummyOF = Objective(rule=OF, sense= minimize)


# Constraints
# AC Power Flow Equations
# C1 Active Power nodal balance

# C2 Reactive Power Nodal Balance

# C3 Voltage angle diff
def angle_ik(model, i, k):
    return model.thetaik[i,k] == model.thetai[i] - model.theta[k]
model.anglediff = Constraint(model.N, model.N, rule=angle_ik)

# C4 Active power balance
def Pi(model, d,g,i):
    return model.Pi[i] == Pdi[]


