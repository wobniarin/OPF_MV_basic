# Requirements: Install pyomo, glpk and gurobi. You should apply for an academic license in gurobi
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np

# Creating the model
model = pyo.ConcreteModel()

model.BusNO = 9
model.BusNumber = pyo.RangeSet(1, 9)
model.BusPQ = pyo.RangeSet(4, 9)
model.BusG = pyo.RangeSet(1, 3)
model.BusSlack = pyo.Param(initialize=1)
model.Line = pyo.RangeSet(1, model.BusNO)
model.Theta = pyo.Var(model.BusNumber)
model.Ploss = pyo.Var(within=pyo.NonNegativeReals)
model.Plij = pyo.Var(model.Line)
model.Qlij = pyo.Var(model.Line)
model.Plji = pyo.Var(model.Line)
model.Qlji = pyo.Var(model.Line)
model.Sbase = pyo.Param(initialize=100)

model.Theta[1].fixed = True
model.Theta[1].value = 0


def Vminmax(model, BusNumber):
    lb = BusData.loc[BusNumber, 'Vmin']
    ub = BusData.loc[BusNumber, 'Vmax']
    return (lb, ub)


model.V = pyo.Var(model.BusNumber, bounds=Vminmax, within=pyo.NonNegativeReals)

model.PG = pyo.Var(model.BusNumber, within=pyo.NonNegativeReals)
for i in model.BusG:
    model.PG[i].setlb(GenData.loc[i, 'Pmin'])
    model.PG[i].setub(GenData.loc[i, 'Pmax'])

for i in model.BusPQ:
    model.PG[i].fixed = True
    model.PG[i].value = 0

model.QG = pyo.Var(model.BusNumber)

for i in model.BusG:
    model.QG[i].setlb(GenData.loc[i, 'Qmin'])
    model.QG[i].setub(GenData.loc[i, 'Qmax'])

for i in model.BusPQ:
    model.QG[i].fixed = True
    model.QG[i].value = 0

model.Sij2 = pyo.Var(model.Line, within=pyo.NonNegativeReals)
for i in model.Line:
    model.Sij2[i].setlb(0)
    model.Sij2[i].setub((LineData.loc[i, 'Smax']) ** 2)

model.Sji2 = pyo.Var(model.Line, within=pyo.NonNegativeReals)
for i in model.Line:
    model.Sji2[i].setlb(0)
    model.Sji2[i].setub((LineData.loc[i, 'Smax']) ** 2)


########
def PowerLoss(model):
    return model.Ploss == model.Sbase * (
                sum(model.PG[i] for i in model.BusG) - sum(BusData.loc[j, 'Pload'] for j in model.BusNumber))


model.PL = pyo.Constraint(rule=PowerLoss)


def P_Bus(model, BusNumber):
    return model.PG[BusNumber] - BusData.loc[BusNumber, 'Pload'] == sum(
        model.V[BusNumber] * model.V[j] * GY.loc[BusNumber, j] * pyo.cos(model.Theta[BusNumber] - model.Theta[j]) +
        BY.loc[BusNumber, j] * pyo.sin(model.Theta[BusNumber] - model.Theta[j]) for j in model.BusNumber if
        (GY.loc[BusNumber, j] != 0 or BY.loc[BusNumber, j] != 0))


model.PBUS = pyo.Constraint(model.BusNumber, rule=P_Bus)


def Q_Bus(model, BusNumber):
    return model.QG[BusNumber] - BusData.loc[BusNumber, 'Qload'] == sum(
        model.V[BusNumber] * model.V[j] * GY.loc[BusNumber, j] * pyo.sin(model.Theta[BusNumber] - model.Theta[j]) -
        BY.loc[BusNumber, j] * pyo.cos(model.Theta[BusNumber] - model.Theta[j]) for j in model.BusNumber if
        (GY.loc[BusNumber, j] != 0 or BY.loc[BusNumber, j] != 0))


model.QBUS = pyo.Constraint(model.BusNumber, rule=Q_Bus)


def P_Line_ij(model, Line):
    return model.Plij[Line] == (LineData.loc[Line, 'GL'] + LineData.loc[Line, 'G0']) * sum(
        Hin.loc[Line, i] * (model.V[i]) ** 2 for i in model.BusNumber if (Hin.loc[Line, i] != 0)) - sum(
        Hin.loc[Line, k] * model.V[k] for k in model.BusNumber if (Hin.loc[Line, k] != 0)) * sum(
        Hout.loc[Line, u] * model.V[u] for u in model.BusNumber if (Hout.loc[Line, u] != 0)) * (
                       (LineData.loc[Line, 'BL']) * pyo.sin(
                   sum(Hin.loc[Line, h] * model.Theta[h] for h in model.BusNumber if (Hin.loc[Line, h] != 0)) - sum(
                       Hout.loc[Line, m] * model.Theta[m] for m in model.BusNumber if (Hout.loc[Line, m] != 0))) + (
                       LineData.loc[Line, 'GL']) * pyo.cos(
                   sum(Hin.loc[Line, n] * model.Theta[n] for n in model.BusNumber if (Hin.loc[Line, n] != 0)) - sum(
                       Hout.loc[Line, z] * model.Theta[z] for z in model.BusNumber if (Hout.loc[Line, z] != 0))))


model.PLINEIJ = pyo.Constraint(model.Line, rule=P_Line_ij)


def Q_Line_ij(model, Line):
    return model.Qlij[Line] == -1.0 * (LineData.loc[Line, 'BL'] + LineData.loc[Line, 'B0']) * sum(
        Hin.loc[Line, i] * (model.V[i]) ** 2 for i in model.BusNumber if (Hin.loc[Line, i] != 0)) + sum(
        Hin.loc[Line, k] * model.V[k] for k in model.BusNumber if (Hin.loc[Line, k] != 0)) * sum(
        Hout.loc[Line, u] * model.V[u] for u in model.BusNumber if (Hout.loc[Line, u] != 0)) * (
                       (LineData.loc[Line, 'BL']) * pyo.cos(
                   sum(Hin.loc[Line, h] * model.Theta[h] for h in model.BusNumber if (Hin.loc[Line, h] != 0)) - sum(
                       Hout.loc[Line, m] * model.Theta[m] for m in model.BusNumber if (Hout.loc[Line, m] != 0))) - (
                       LineData.loc[Line, 'GL']) * pyo.sin(
                   sum(Hin.loc[Line, n] * model.Theta[n] for n in model.BusNumber if (Hin.loc[Line, n] != 0)) - sum(
                       Hout.loc[Line, z] * model.Theta[z] for z in model.BusNumber if (Hout.loc[Line, z] != 0))))


model.QLINEIJ = pyo.Constraint(model.Line, rule=Q_Line_ij)


def S_Line_ij(model, Line):
    return model.Sij2[Line] == ((model.Plij[Line]) ** 2 + (model.Qlij[Line]) ** 2)


model.SIJ2 = pyo.Constraint(model.Line, rule=S_Line_ij)


def P_Line_ji(model, Line):
    return model.Plji[Line] == (LineData.loc[Line, 'GL'] + LineData.loc[Line, 'G0']) * sum(
        Hout.loc[Line, i] * (model.V[i]) ** 2 for i in model.BusNumber if (Hout.loc[Line, i] != 0)) - sum(
        Hout.loc[Line, k] * model.V[k] for k in model.BusNumber if (Hout.loc[Line, k] != 0)) * sum(
        Hin.loc[Line, u] * model.V[u] for u in model.BusNumber if (Hin.loc[Line, u] != 0)) * (
                       (LineData.loc[Line, 'BL']) * pyo.sin(
                   sum(Hout.loc[Line, h] * model.Theta[h] for h in model.BusNumber if (Hout.loc[Line, h] != 0)) - sum(
                       Hin.loc[Line, m] * model.Theta[m] for m in model.BusNumber if (Hin.loc[Line, m] != 0))) + (
                       LineData.loc[Line, 'GL']) * pyo.cos(
                   sum(Hout.loc[Line, n] * model.Theta[n] for n in model.BusNumber if (Hout.loc[Line, n] != 0)) - sum(
                       Hin.loc[Line, z] * model.Theta[z] for z in model.BusNumber if (Hin.loc[Line, z] != 0))))


model.PLINEJI = pyo.Constraint(model.Line, rule=P_Line_ji)


def Q_Line_ji(model, Line):
    return model.Qlji[Line] == -1.0 * (LineData.loc[Line, 'BL'] + LineData.loc[Line, 'B0']) * sum(
        Hout.loc[Line, i] * (model.V[i]) ** 2 for i in model.BusNumber if (Hout.loc[Line, i] != 0)) + sum(
        Hout.loc[Line, k] * model.V[k] for k in model.BusNumber if (Hout.loc[Line, k] != 0)) * sum(
        Hin.loc[Line, u] * model.V[u] for u in model.BusNumber if (Hin.loc[Line, u] != 0)) * (
                       (LineData.loc[Line, 'BL']) * pyo.cos(
                   sum(Hout.loc[Line, h] * model.Theta[h] for h in model.BusNumber if (Hout.loc[Line, h] != 0)) - sum(
                       Hin.loc[Line, m] * model.Theta[m] for m in model.BusNumber if (Hin.loc[Line, m] != 0))) - (
                       LineData.loc[Line, 'GL']) * pyo.sin(
                   sum(Hout.loc[Line, n] * model.Theta[n] for n in model.BusNumber if (Hout.loc[Line, n] != 0)) - sum(
                       Hin.loc[Line, z] * model.Theta[z] for z in model.BusNumber if (Hin.loc[Line, z] != 0))))


model.QLINEji = pyo.Constraint(model.Line, rule=Q_Line_ji)


def S_Line_ji(model, Line):
    return model.Sji2[Line] == ((model.Plji[Line]) ** 2 + (model.Qlji[Line]) ** 2)


model.SJI2 = pyo.Constraint(model.Line, rule=S_Line_ji)


def ThermalCost(model):
    return sum((GenData.loc[i, 'a'] * ((model.PG[i] * model.Sbase) ** 2)) + (
                GenData.loc[i, 'b'] * (model.PG[i] * model.Sbase)) + GenData.loc[i, 'c'] for i in model.BusG)


model.OF = pyo.Objective(rule=ThermalCost, sense=pyo.minimize)

opt = SolverFactory('knitro')
opt.solve(model)