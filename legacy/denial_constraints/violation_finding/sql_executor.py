import duckdb
from pandas import DataFrame

from denial_constraints.entities.workload import Workload


def execute_sql(workload: Workload) -> DataFrame:
    t1_data, t2_data, query = workload
    with duckdb.connect() as connection:
        connection.execute("PRAGMA threads=4")
        connection.register("t1_data", t1_data)
        connection.register("t2_data", t2_data)

        return connection.execute(query).df()
