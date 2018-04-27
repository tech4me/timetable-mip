from helper import *
from gurobipy import *

ECE342 = Course('ECE342H1S20181')
ECE344 = Course('ECE344H1S20181')
ECE521 = Course('ECE521H1S20181')
APS420 = Course('APS420H1S20181')

course_list = [ECE342, ECE344, ECE521]
#course_list = [ECE342, ECE344, ECE521, APS420]

meeting_sections_count = 0
for i in range(len(course_list)):
    meeting_sections_count += course_list[i].meeting_sections_count

try:
    # Create a new model
    m = Model("timetable-mip")

    # Variable helper table
    # 5 days in a week and 24 slots every day
    T = [[[None]*meeting_sections_count for _ in range(24)] for _ in range(5)]
    V = []

    # Create variables
    previous_i_end = 0
    for course_index in range(len(course_list)):
        # Create variables
        s = course_list[course_index].meeting_sections_slots;

        v_c = []
        for i in range(len(s)):
            v = m.addVar(vtype=GRB.BINARY, name="{}_{}".format(course_list[course_index].course_code, course_list[course_index].meeting_sections_codes[i]))
            v_c.append(v)
            for j in s[i]:
                d = j[0]
                for k in j[1]:
                    T[d][k][i + previous_i_end] = v
        V.append(v_c)
        previous_i_end = len(s)

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
            if count > 1:
                m.addConstr(l, GRB.LESS_EQUAL, 1)

    # Constraint: Course Taken (for courses that are must take)
    for course_index in range(len(course_list)):
        s = course_list[course_index].meeting_sections_sets;
        for i in range(len(s)):
            l = LinExpr()
            count = 0
            for j in range(len(V[course_index])):
                if j in s[i]:
                    l.add(V[course_index][j])
                    count += 1
            if count != 0:
                m.addConstr(l, GRB.EQUAL, 1)

    # Constraint: Course Meeting Section Exclusivity
        for i in range(len(s)):
            l = LinExpr()
            count = 0
            for j in range(len(V[course_index])):
                if j in s[i]:
                    l.add(V[course_index][j])
                    count += 1
            if count > 1:
                m.addConstr(l, GRB.LESS_EQUAL, 1)

    # Set objectives

    m.write("test.lp")
    m.optimize()

    if m.status == GRB.OPTIMAL:
        for v in m.getVars():
            print(v.varName, v.x)
        print('Obj:', m.objVal)

except GurobiError:
    print('Error reported')
