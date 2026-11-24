import gurobipy as gp
from gurobipy import GRB
import json

# Dati del problema
progetti = ['P1','P2','P3','P4','P5','P6','P7','P8']
valore = {'P1':30,'P2':24,'P3':35,'P4':28,'P5':33,'P6':26,'P7':38,'P8':21}
budget = {'P1':20,'P2':18,'P3':27,'P4':24,'P5':22,'P6':19,'P7':30,'P8':15}
personale = {'P1':4,'P2':3,'P3':5,'P4':4,'P5':4,'P6':3,'P7':5,'P8':2}

B_max = 100
P_max = 18

# Creazione modello
m = gp.Model("Selezione_Portafoglio")

# Variabili decisionali binarie
x = m.addVars(progetti, vtype=GRB.BINARY, name="x")

# Funzione obiettivo: massimizzare il valore totale
m.setObjective(gp.quicksum(valore[i]*x[i] for i in progetti), GRB.MAXIMIZE)

# Vincolo di budget
m.addConstr(gp.quicksum(budget[i]*x[i] for i in progetti) <= B_max, name="Budget")

# Vincolo di personale
m.addConstr(gp.quicksum(personale[i]*x[i] for i in progetti) <= P_max, name="Personale")

# P5 richiede P2
m.addConstr(x['P5'] <= x['P2'], name="P5_richiede_P2")

# P7 richiede P3
m.addConstr(x['P7'] <= x['P3'], name="P7_richiede_P3")

# P4 e P6 incompatibili
m.addConstr(x['P4'] + x['P6'] <= 1, name="P4_P6_incompatibili")

# Almeno un progetto digitale tra P1, P3, P7
m.addConstr(x['P1'] + x['P3'] + x['P7'] >= 1, name="Digitale_minimo")

# Almeno tre progetti complessivi
m.addConstr(gp.quicksum(x[i] for i in progetti) >= 3, name="Minimo_tre_progetti")

# Risoluzione
m.optimize()

# Estrazione risultati
if m.status == GRB.OPTIMAL:
    status_str = "OPTIMAL"
    obj_val = m.objVal
    variables = {f"x_{i}": x[i].X for i in progetti}
else:
    status_str = str(m.status)
    obj_val = None
    variables = {}

# Output finale
result = {
    "status": status_str,
    "objective": obj_val,
    "variables": variables
}

print("SOLUTION_JSON=" + json.dumps(result))
