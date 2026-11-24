import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
zones = ["Z1","Z2","Z3","Z4","Z5","Z6","Z7","Z8"]
sites = ["A","B","C","D","E","F"]
north = ["A","B","C"]
south = ["D","E","F"]

demand = {"Z1":30,"Z2":25,"Z3":35,"Z4":20,"Z5":28,"Z6":32,"Z7":24,"Z8":26}

fixed_cost = {"A":110,"B":95,"C":120,"D":90,"E":105,"F":100}
capacity   = {"A":90,"B":80,"C":110,"D":75,"E":95,"F":85}

unit_cost = {
    "Z1": {"A":4,"B":7,"C":6,"D":10,"E":9,"F":11},
    "Z2": {"A":5,"B":4,"C":8,"D":9,"E":7,"F":10},
    "Z3": {"A":7,"B":5,"C":4,"D":8,"E":9,"F":7},
    "Z4": {"A":9,"B":8,"C":7,"D":4,"E":5,"F":6},
    "Z5": {"A":8,"B":9,"C":6,"D":5,"E":4,"F":7},
    "Z6": {"A":10,"B":8,"C":7,"D":6,"E":5,"F":4},
    "Z7": {"A":6,"B":7,"C":5,"D":8,"E":6,"F":7},
    "Z8": {"A":7,"B":6,"C":8,"D":5,"E":7,"F":4},
}

emission = {
    "Z1": {"A":1,"B":2,"C":2,"D":4,"E":3,"F":4},
    "Z2": {"A":2,"B":1,"C":3,"D":3,"E":2,"F":4},
    "Z3": {"A":3,"B":2,"C":1,"D":3,"E":4,"F":3},
    "Z4": {"A":4,"B":3,"C":3,"D":1,"E":2,"F":2},
    "Z5": {"A":3,"B":4,"C":2,"D":2,"E":1,"F":3},
    "Z6": {"A":4,"B":3,"C":3,"D":2,"E":2,"F":1},
    "Z7": {"A":2,"B":3,"C":1,"D":3,"E":2,"F":3},
    "Z8": {"A":3,"B":2,"C":3,"D":1,"E":3,"F":1},
}

MIN_THROUGHPUT = 20
E_MAX = 470
N_MIN, N_MAX = 3, 4

# ---------------- Modello ----------------
m = gp.Model("H01_rete_distributiva")
m.Params.OutputFlag = 0

y = m.addVars(sites, vtype=GRB.BINARY, name="y")
x = m.addVars(sites, zones, lb=0.0, vtype=GRB.CONTINUOUS, name="x")

# Obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[i]*y[i] for i in sites) +
    gp.quicksum(unit_cost[j][i]*x[i,j] for i in sites for j in zones),
    GRB.MINIMIZE
)

# Domanda soddisfatta integralmente
for j in zones:
    m.addConstr(gp.quicksum(x[i,j] for i in sites) == demand[j], name=f"dom_{j}")

# Capacità legata all'apertura
for i in sites:
    m.addConstr(gp.quicksum(x[i,j] for j in zones) <= capacity[i]*y[i], name=f"cap_{i}")

# Movimentazione minima se aperto
for i in sites:
    m.addConstr(gp.quicksum(x[i,j] for j in zones) >= MIN_THROUGHPUT*y[i], name=f"min_{i}")

# Numero di centri aperti
m.addConstr(gp.quicksum(y[i] for i in sites) >= N_MIN, name="n_min")
m.addConstr(gp.quicksum(y[i] for i in sites) <= N_MAX, name="n_max")

# Almeno un centro per gruppo
m.addConstr(gp.quicksum(y[i] for i in north) >= 1, name="north_open")
m.addConstr(gp.quicksum(y[i] for i in south) >= 1, name="south_open")

# Vincolo emissioni
m.addConstr(
    gp.quicksum(emission[j][i]*x[i,j] for i in sites for j in zones) <= E_MAX,
    name="emission_cap"
)

m.optimize()

# ---------------- Output ----------------
status_map = {GRB.OPTIMAL: "OPTIMAL"}
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.objVal, 4)
    variables = {}
    for i in sites:
        variables[f"y_{i}"] = round(y[i].X, 4)
    for i in sites:
        for j in zones:
            variables[f"x_{i}_{j}"] = round(x[i,j].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(m.status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
