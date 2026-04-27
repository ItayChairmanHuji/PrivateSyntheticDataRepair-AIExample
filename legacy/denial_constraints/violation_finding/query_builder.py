from denial_constraints.entities.denial_constraint import DenialConstraint


def build_constraint_query(constraint: DenialConstraint) -> str:
    join_conditions, post_join_conditions = _create_conditions(constraint)
    where_clause = _build_where_clause(post_join_conditions)
    return _build_query(join_conditions, where_clause)


def _create_conditions(constraint: DenialConstraint):
    join_conditions = ["t1.idx != t2.idx"]
    post_join_conditions: list[str] = []

    for predicate in constraint.cross_predicates:
        if predicate.opr == "=":
            join_conditions.append(predicate.sql)
        else:
            post_join_conditions.append(predicate.sql)
    return join_conditions, post_join_conditions


def _build_where_clause(post_join_condition):
    return "WHERE " + " AND ".join(post_join_condition) if post_join_condition else ""


def _build_query(join_conditions, where_clause):
    return ("SELECT t1.idx - 1 AS id1, t2.idx - 1 AS id2\n"
            "FROM t1_data AS t1\n"
            "JOIN t2_data AS t2\n"
            "  ON " + " AND ".join(join_conditions) + "\n" + where_clause)
