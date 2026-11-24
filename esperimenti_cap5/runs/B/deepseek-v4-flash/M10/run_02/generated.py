import gurobipy as gp
from gurobipy import GRB
import json

archi = [
    ("S", "A", 40, 2, 30),
    ("S", "B", 35, 3, 35),
    ("A", "B", 15, 1, 15),
    ("A", "C", 30, 2, 25),
    ("B", "C", 18, 2, 20),
    ("B", "T", 45, 4, 25),
    ("C", "T", 38, 2, 35),
]

nodi = ["S", "A", "B", "C", "T"]
domanda = {"S": 40, "A": 0, "B": 0, "C": 0, "T": -40}

m = gp.Model("rete_distributiva")
m.setParam("OutputFlag", 0)

x = {}
y = {}

for i, j, f, c, q in archi:
    x[(i, j)] = m.addVar(lb=0, ub=q, vtype=GRB.INTEGER, name=f"x_{i}_{j}")
    y[(i, j)] = m.addVar(vtype=GRB.BINARY, name=f"y_{i}_{j}")

m.setObjective(
    gp.quicksum(f * y[(i, j)] + c * x[(i, j)] for i, j, f, c, q in archi),
    GRB.MINIMIZE
)

for n in nodi:
    uscita = gp.quicksum(x[(i, j)] for i, j, _, _, _ in archi if i == n)
    entrata = gp.quicksum(x[(i, j)] for i, j, _, _, _ in archi if j == n)
    m.addConstr(uscita - entrata == domanda[n], name=f"flusso_{n}")

for i, j, _, _, q in archi:
    m.addConstr(x[(i, j)] <= q * y[(i, j)], name=f"capacita_{i}_{j}")

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {v.VarName: float(v.X) for v in m.getVars()}
else:
    if m.status == GRB.INFEASIBLE:
        status = "INFEASIBLE"
    elif m.status == GRB.UNBOUNDED:
        status = "UNBOUNDED"
    else:
        status = f"STATUS_{m.status}"
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": objective, "variables": variables},
    separators=(",", ":")
))
