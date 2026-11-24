import gurobipy as gp
from gurobipy import GRB

suppliers = ['A','B','C','D','E','F']
components = ['C1','C2','C3']

demand = {'C1':80,'C2':70,'C3':60}
fixed  = {'A':120,'B':140,'C':100,'D':150,'E':90,'F':110}
cap    = {'A':100,'B':110,'C':90,'D':120,'E':80,'F':95}
risk   = {'A':2,'B':3,'C':1,'D':4,'E':2,'F':3}

cost = {
    ('A','C1'):9, ('A','C2'):12, ('A','C3'):11,
    ('B','C1'):10,('B','C2'):9,  ('B','C3'):12,
    ('C','C1'):11,('C','C2'):10, ('C','C3'):9,
                 ('D','C2'):11, ('D','C3'):10,
    ('E','C1'):12,('E','C2'):8,
    ('F','C1'):10,               ('F','C3'):8,
}

quality = {
    ('A','C1'):96, ('A','C2'):94, ('A','C3'):95,
    ('B','C1'):93, ('B','C2'):97, ('B','C3'):92,
    ('C','C1'):98, ('C','C2'):95, ('C','C3'):96,
                    ('D','C2'):94, ('D','C3'):93,
    ('E','C1'):97, ('E','C2'):98,
    ('F','C1'):94,                ('F','C3'):98,
}

S = list(cost.keys())

m = gp.Model("H07_sourcing")
m.Params.OutputFlag = 0

x = m.addVars(S, vtype=GRB.INTEGER, lb=0, name="x")
z = m.addVars(S, vtype=GRB.BINARY, name="z")
y = m.addVars(suppliers, vtype=GRB.BINARY, name="y")

# 1. Domanda esatta
for k in components:
    m.addConstr(
        gp.quicksum(x[i,k] for i in suppliers if (i,k) in cost) == demand[k],
        name=f"demand_{k}"
    )

# 2. Legame quantità-uso e minimo 10 unità
for (i,k) in S:
    M_ik = min(cap[i], demand[k])
    m.addConstr(x[i,k] <= M_ik * z[i,k], name=f"bigM_{i}_{k}")
    m.addConstr(x[i,k] >= 10 * z[i,k], name=f"min10_{i}_{k}")

# 3. Almeno 2 fornitori per componente
for k in components:
    m.addConstr(
        gp.quicksum(z[i,k] for i in suppliers if (i,k) in cost) >= 2,
        name=f"multisource_{k}"
    )

# 4. Capacità complessiva per fornitore
for i in suppliers:
    m.addConstr(
        gp.quicksum(x[i,k] for k in components if (i,k) in cost) <= cap[i]*y[i],
        name=f"cap_{i}"
    )

# 5. Coerenza uso-attivazione
for (i,k) in S:
    m.addConstr(z[i,k] <= y[i], name=f"link_{i}_{k}")

# 6. Massimo 4 fornitori attivi
m.addConstr(gp.quicksum(y[i] for i in suppliers) <= 4, name="max_suppliers")

# 7. Almeno uno tra A e B
m.addConstr(y['A'] + y['B'] >= 1, name="A_or_B")

# 8. Qualità media minima
for k in components:
    m.addConstr(
        gp.quicksum(quality[i,k]*x[i,k] for i in suppliers if (i,k) in cost) >= 95*demand[k],
        name=f"quality_{k}"
    )

# 9. Rischio totale massimo
m.addConstr(
    gp.quicksum(risk[i]*x[i,k] for (i,k) in S) <= 580,
    name="risk_total"
)

# Obiettivo
m.setObjective(
    gp.quicksum(cost[i,k]*x[i,k] for (i,k) in S) +
    gp.quicksum(fixed[i]*y[i] for i in suppliers),
    GRB.MINIMIZE
)

m.optimize()

status = m.Status
if status == GRB.OPTIMAL:
    variables = {}
    for (i,k) in S:
        variables[f"x_{i}_{k}"] = x[i,k].X
        variables[f"z_{i}_{k}"] = z[i,k].X
    for i in suppliers:
        variables[f"y_{i}"] = y[i].X
    obj = m.ObjVal
    print(f'SOLUTION_JSON={{"status":"OPTIMAL","objective":{obj},"variables":{variables}}}')
else:
    print(f'SOLUTION_JSON={{"status":"{status}","objective":null,"variables":{{}}}}')
