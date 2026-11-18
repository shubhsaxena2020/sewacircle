import sys
import ortools
from ortools.sat.python import cp_model
print("PYTHON", sys.version)
print("ORTOOLS", ortools.__version__)
print("HAS_CPMODEL", cp_model.CpModel.__name__)
print("OPTIMAL", cp_model.OPTIMAL, "FEASIBLE", cp_model.FEASIBLE, "INFEASIBLE", cp_model.INFEASIBLE)
