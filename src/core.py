from helper import *
from gurobipy import *

ECE311 = Course('ECE311H1S20181')
ECE334 = Course('ECE334H1S20181')
ECE342 = Course('ECE342H1S20181')
ECE344 = Course('ECE344H1S20181')
ECE361 = Course('ECE361H1S20181')
ECE472 = Course('ECE472H1S20181')
ECE521 = Course('ECE521H1S20181')
APS420 = Course('APS420H1S20181')
APS321 = Course('APS321H1S20181')
CSC343 = Course('CSC343H5S20181')

mandatory_course_list = [ECE311, ECE334, ECE342, ECE344, ECE361, ECE521]
optional_course_list = [ECE472, APS420, APS321, CSC343]
course_list = mandatory_course_list + optional_course_list

num_course_from_optional = 2

meeting_sections_count = 0
for i in range(len(course_list)):
    meeting_sections_count += course_list[i].meeting_sections_count

try:
    # Create a new model
    m = Model("timetable-mip")

    # Variable helper table
    # T is a table of gurobi variables weight is 5, height is 24, and depth is the number of total meeting sections
    T = [[[None]*meeting_sections_count for _ in range(24)] for _ in range(5)]
    # V is a two-dimensional list of gurobi variables, the first dimension is course, the second dimentsion is the meeting sections in that course
    V = []
    # V_M is the mandatory subset of V
    V_M = []
    # V_O is the optional subset of V
    V_O = []
    # V_O_H is a helper list for the optional course count constraint
    V_O_H = []

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
        if course_list[course_index] in mandatory_course_list:
            V_M.append(v_c)
        elif course_list[course_index] in optional_course_list:
            V_O.append(v_c)
            V_O_H.append(m.addVar(vtype=GRB.BINARY, name="{}_helper".format(course_list[course_index].course_code)))
        previous_i_end = len(s)
    m.update()

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

    # Constraint: Course Taken (Mandatory)
    for course_index in range(len(mandatory_course_list)):
        s = mandatory_course_list[course_index].meeting_sections_sets;
        for i in range(len(s)):
            l = LinExpr()
            count = 0
            for j in range(len(V_M[course_index])):
                if j in s[i]:
                    l.add(V_M[course_index][j])
                    count += 1
            if count != 0:
                m.addConstr(l, GRB.EQUAL, 1)

    # Constraint: Course Taken (Optional)
    for course_index in range(len(optional_course_list)):
        s = optional_course_list[course_index].meeting_sections_sets;
        for i in range(len(s)):
            l = LinExpr()
            count = 0
            for j in range(len(V_O[course_index])):
                if j in s[i]:
                    l.add(V_O[course_index][j])
                    count += 1
            if count != 0:
                m.addConstr((V_O_H[course_index] == 1) >> (l == 1))

    # Constraint: Course Meeting Section Exclusivity
    for course_index in range(len(course_list)):
        s = course_list[course_index].meeting_sections_sets;
        for i in range(len(s)):
            l = LinExpr()
            count = 0
            for j in range(len(V[course_index])):
                if j in s[i]:
                    l.add(V[course_index][j])
                    count += 1
            if count > 1:
                m.addConstr(l, GRB.LESS_EQUAL, 1)

    # Constraint: Optional Course Count
    for course_index in range(len(optional_course_list)):
        m.addConstr(V_O_H[course_index] == or_(V_O[course_index]))
    l = LinExpr()
    for course_index in range(len(optional_course_list)):
        l.add(V_O_H[course_index])
    m.addConstr(l, GRB.EQUAL, num_course_from_optional)

    # Set objectives

    m.write("test.lp")
    m.optimize()

    if m.status == GRB.OPTIMAL:
        for v in m.getVars():
            print(v.varName, v.x)
        print('Obj:', m.objVal)

except GurobiError as e:
    print(e.message)
