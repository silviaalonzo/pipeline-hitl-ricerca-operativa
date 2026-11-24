import gurobipy as gp
from gurobipy import GRB
import json

inspectors = ["I1","I2","I3","I4","I5","I6","I7","I8","I9","I10","I11","I12"]
audits = ["A01","A02","A03","A04","A05","A06","A07","A08","A09","A10",
          "A11","A12","A13","A14","A15","A16","A17","A18","A19","A20"]

senior = {"I1","I2","I3","I4"}
high_risk = {"A04","A08","A12","A16","A20"}

fixed_cost = {
    "I1":18,"I2":23,"I3":28,"I4":22,"I5":27,"I6":21,
    "I7":26,"I8":20,"I9":25,"I10":19,"I11":24,"I12":18
}

max_hours = {
    "I1":13,"I2":14,"I3":15,"I4":16,"I5":17,"I6":13,
    "I7":14,"I8":15,"I9":16,"I10":17,"I11":13,"I12":14
}

max_audits = {
    "I1":3,"I2":3,"I3":3,"I4":3,"I5":4,"I6":4,
    "I7":4,"I8":4,"I9":4,"I10":4,"I11":4,"I12":4
}

duration = {
    "A01":3,"A02":4,"A03":2,"A04":6,"A05":5,"A06":3,"A07":4,"A08":7,
    "A09":2,"A10":5,"A11":3,"A12":6,"A13":4,"A14":2,"A15":5,"A16":7,
    "A17":3,"A18":4,"A19":5,"A20":6
}

demand = {a: 1 for a in audits}
for a in high_risk:
    demand[a] = 2

cost = {
    "I1":  {"A01":None,"A02":6,"A03":9,"A04":12,"A05":None,"A06":18,"A07":8,"A08":11,"A09":14,"A10":17,
            "A11":7,"A12":10,"A13":13,"A14":16,"A15":None,"A16":9,"A17":12,"A18":15,"A19":None,"A20":8},
    "I2":  {"A01":10,"A02":13,"A03":None,"A04":6,"A05":9,"A06":None,"A07":15,"A08":18,"A09":8,"A10":None,
            "A11":14,"A12":17,"A13":None,"A14":10,"A15":13,"A16":16,"A17":None,"A18":9,"A19":12,"A20":15},
    "I3":  {"A01":None,"A02":7,"A03":10,"A04":13,"A05":16,"A06":6,"A07":9,"A08":12,"A09":15,"A10":18,
            "A11":None,"A12":11,"A13":14,"A14":17,"A15":None,"A16":10,"A17":13,"A18":None,"A19":6,"A20":9},
    "I4":  {"A01":11,"A02":None,"A03":17,"A04":7,"A05":10,"A06":None,"A07":16,"A08":6,"A09":None,"A10":12,
            "A11":15,"A12":18,"A13":None,"A14":11,"A15":14,"A16":17,"A17":7,"A18":10,"A19":13,"A20":16},
    "I5":  {"A01":18,"A02":8,"A03":11,"A04":None,"A05":17,"A06":7,"A07":None,"A08":13,"A09":16,"A10":6,
            "A11":None,"A12":12,"A13":15,"A14":None,"A15":8,"A16":11,"A17":14,"A18":None,"A19":7,"A20":10},
    "I6":  {"A01":12,"A02":None,"A03":18,"A04":8,"A05":None,"A06":14,"A07":17,"A08":7,"A09":None,"A10":13,
            "A11":16,"A12":None,"A13":9,"A14":12,"A15":15,"A16":None,"A17":8,"A18":11,"A19":None,"A20":17},
    "I7":  {"A01":6,"A02":9,"A03":None,"A04":15,"A05":18,"A06":8,"A07":None,"A08":14,"A09":17,"A10":None,
            "A11":10,"A12":13,"A13":16,"A14":None,"A15":9,"A16":12,"A17":None,"A18":18,"A19":8,"A20":11},
    "I8":  {"A01":None,"A02":16,"A03":6,"A04":9,"A05":None,"A06":15,"A07":18,"A08":None,"A09":11,"A10":14,
            "A11":17,"A12":None,"A13":10,"A14":13,"A15":None,"A16":6,"A17":9,"A18":12,"A19":None,"A20":18},
    "I9":  {"A01":7,"A02":10,"A03":None,"A04":16,"A05":6,"A06":None,"A07":12,"A08":15,"A09":18,"A10":None,
            "A11":11,"A12":14,"A13":None,"A14":7,"A15":10,"A16":13,"A17":None,"A18":6,"A19":9,"A20":None},
    "I10": {"A01":None,"A02":17,"A03":7,"A04":None,"A05":13,"A06":16,"A07":6,"A08":None,"A09":12,"A10":15,
            "A11":None,"A12":8,"A13":11,"A14":14,"A15":None,"A16":7,"A17":10,"A18":None,"A19":16,"A20":6},
    "I11": {"A01":8,"A02":None,"A03":14,"A04":17,"A05":7,"A06":None,"A07":13,"A08":16,"A09":None,"A10":9,
            "A11":12,"A12":15,"A13":None,"A14":8,"A15":11,"A16":None,"A17":17,"A18":7,"A19":10,"A20":None},
    "I12": {"A01":15,"A02":18,"A03":8,"A04":None,"A05":14,"A06":17,"A07":None,"A08":10,"A09":13,"A10":16,
            "A11":None,"A12":9,"A13":12,"A14":None,"A15":18,"A16":8,"A17":11,"A18":None,"A19":17,"A20":7}
}

allowed = [(i,j) for i in inspectors for j in audits if cost[i][j] is not None]

model = gp.Model("audit_assignment")
model.setParam("OutputFlag", 0)

x = {}
for (i,j) in allowed:
    x[i,j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

y = {}
for i in inspectors:
    y[i] = model.addVar(vtype=GRB.BINARY, name=f"y_{i}")

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in inspectors) +
    gp.quicksum(cost[i][j] * x[i,j] for (i,j) in allowed),
    GRB.MINIMIZE
)

# Copertura esatta di ogni audit
for j in audits:
    model.addConstr(
        gp.quicksum(x[i,j] for i in inspectors if (i,j) in allowed) == demand[j],
        name=f"cover_{j}"
    )

# Almeno un senior per audit ad alto rischio
for j in high_risk:
    model.addConstr(
        gp.quicksum(x[i,j] for i in senior if (i,j) in allowed) >= 1,
        name=f"senior_{j}"
    )

# Legame assegnazione-attivazione e capacità
for i in inspectors:
    for j in audits:
        if (i,j) in allowed:
            model.addConstr(x[i,j] <= y[i], name=f"link_{i}_{j}")

    model.addConstr(
        gp.quicksum(duration[j] * x[i,j] for j in audits if (i,j) in allowed) <= max_hours[i] * y[i],
        name=f"hours_{i}"
    )
    model.addConstr(
        gp.quicksum(x[i,j] for j in audits if (i,j) in allowed) <= max_audits[i] * y[i],
        name=f"audits_{i}"
    )
    model.addConstr(
        y[i] <= gp.quicksum(x[i,j] for j in audits if (i,j) in allowed),
        name=f"use_{i}"
    )

# Massimo dieci ispettori attivati
model.addConstr(gp.quicksum(y[i] for i in inspectors) <= 10, name="max_inspectors")

# Incompatibilità per ispettore
incompatible_pairs = [("A01","A02"),("A06","A07"),("A11","A12"),("A17","A18")]
for i in inspectors:
    for (a,b) in incompatible_pairs:
        if (i,a) in allowed and (i,b) in allowed:
            model.addConstr(x[i,a] + x[i,b] <= 1, name=f"incomp_{i}_{a}_{b}")

model.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD"
}

if model.status == GRB.OPTIMAL:
    solution = {
        "status": "OPTIMAL",
        "objective": model.ObjVal,
        "variables": {v.VarName: v.X for v in model.getVars()}
    }
else:
    solution = {
        "status": status_map.get(model.status, str(model.status)),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(solution, separators=(",", ":")))
