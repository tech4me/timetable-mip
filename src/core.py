from helper import *
from gurobipy import *

c = Course()

try:
    # Create a new model
    m = Model("timetable-mip")

    meeting_sections_count = c.meeting_sections_count

    # Variable helper table
    # 5 days in a week and 24 slots every day
    T = [[[None]*meeting_sections_count for _ in range(24)] for _ in range(5)]
    V = []

    # Create variables
    # Course data
    s = c.get_meeting_sections_slots();
    for i in range(len(s)):
        v = m.addVar(vtype=GRB.BINARY, name="V_{}".format(i))
        V.append(v)
        for j in s[i]:
            d = j[0]
            for k in j[1]:
                T[d][k][i] = v

    # Add constraints
    # Constraint: Time Slot Exclusivity
    for i in range(5):
        for j in range(24):
            l = LinExpr()
            count = 0
            for k in range(meeting_sections_count):
                if T[i][j][k] is not None:
                    l.add(T[i][j][k])
                    count += 1
            if count != 0:
                m.addConstr(l, GRB.LESS_EQUAL, 1)

    # Constraint: Course Taken (for course that are must take)
    s = c.get_meeting_sections_sets()
    for i in range(len(s)):
        l = LinExpr()
        count = 0
        for j in range(len(V)):
            if j in s[i]:
                l.add(V[j])
                count += 1
        if count != 0:
            m.addConstr(l, GRB.EQUAL, 1)

    # Constraint: Course Meeting Section Exclusivity
    for i in range(len(s)):
        c_var = []
        for j in range(len(V)):
            if j in s[i]:
                c_var.append(V[j])
        if len(c_var) != 0:
            m.addSOS(GRB.SOS_TYPE1, c_var)

    # Set objectives

    m.write("test.lp")
    m.optimize()

    if m.status == GRB.OPTIMAL:
        for v in m.getVars():
            print(v.varName, v.x)
        print('Obj:', m.objVal)

except GurobiError:
    print('Error reported')
