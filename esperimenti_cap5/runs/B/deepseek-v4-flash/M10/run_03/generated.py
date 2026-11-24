import gurobipy as gp
from gurobipy import GRB
import json

arcs = {
    "SA": {"tail": "S", "head": "A", "fisso": 40, "unitario": 2, "capacita": 30},
    "SB": {"tail": "S", "head": "B", "fisso": 35, "unitario": 3, "capacita": 35},
    "AB": {"tail": "A", "head": "B", "fisso": 15, "unitario": 1, "capacita": 15},
    "AC": {"tail": "A", "head": "C", "fisso": 30, "unitario": 2, "capacita": 25},
    "BC": {"tail": "B", "head": "C", "fisso": 18, "unitario": 2, "capacita": 20},
    "BT": {"tail": "B", "head": "T", "fisso": 45, "unitario": 4, "capacita": 25},
    "CT": {"tail": "C", "head": "T", "fisso": 38, "unitario": 2, "capacita": 35},
}

nodi = ["S", "A", "B", "C", "T"]
bilancio = {"S": 40, "A": 0, "B": 0, "C": 0, "T": -40}

model = gp.Model("rete_distributiva")
model.Params.OutputFlag = 0

x = {}
y = {}

for a in arcs:
    x[a] = model.addVar(lb=0, vtype=GRB.INTEGER, name=f"x_{a}")
    y[a] = model.addVar(lb=0, vtype=GRB.BINARY, name=f"y_{a}")

model.setObjective(
    gp.quicksum(arcs[a]["fisso"] * y[a] + arcs[a]["unitario"] * x[a] for a in arcs),
    GRB.MINIMIZE
)

# Capacità e attivazione
for a in arcs:
    model.addConstr(x[a] <= arcs[a]["capacita"] * y[a], name=f"cap_{a}")

# Conservazione del flusso
out_arcs = {n: [] for n in nodi}
in_arcs = {n: [] for n in nodi}

for a, d in arcs.items():
    out_arcs[d["tail"]].append(a)
    in_arcs[d["head"]].append(a)

for n in nodi:
    model.addConstr(
        gp.quicksum(x[a] for a in out_arcs[n]) - gp.quicksum(x[a] for a in in_arcs[n]) == bilancio[n],
        name=f"flow_{n}"
    )

model.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
}

status = status_map.get(model.status, str(model.status))

if model.status == GRB.OPTIMAL:
    obj = model.ObjVal
    vars_dict = {v.VarName: v.X for v in model.getVars()}
else:
    obj = None
    vars_dict = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": obj, "variables": vars_dict},
    separators=(",", ":")
))
