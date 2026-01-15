import json
import numpy as np


def read_json_file(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = f.read()
    return data.strip()


def membership(x, points):
    if not points or len(points) < 2:
        return 0.0

    pts = sorted(points, key=lambda v: v[0])
    xs, ys = zip(*pts)

    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]

    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        if x1 <= x <= x2:
            if x2 == x1:
                return (y1 + y2) * 0.5
            k = (y2 - y1) / (x2 - x1)
            return y1 + k * (x - x1)

    return 0.0


def fuzzify(value, ling_var):
    memberships = {}
    for term in ling_var:
        memberships[term["id"]] = membership(value, term["points"])
    return memberships


def get_output_range(control_ling_var):
    xs = [
        x
        for term in control_ling_var
        for x, _ in term.get("points", [])
    ]

    if not xs:
        return 0, 10

    return min(xs), max(xs)


def aggregate_membership(activations, rules, control_ling_var, s_values):
    aggregated = np.zeros_like(s_values, dtype=float)

    for level, rule in zip(activations, rules):
        _, out_id = rule
        if level <= 0:
            continue

        term = next(
            (t for t in control_ling_var if t["id"] == out_id),
            None
        )
        if term is None:
            continue

        mu = np.array(
            [membership(s, term["points"]) for s in s_values]
        )
        aggregated = np.maximum(aggregated, np.minimum(level, mu))

    return aggregated


def defuzzify_mean_of_max(s_values, mu_agg):
    if mu_agg.size == 0:
        return 0.0

    peak = mu_agg.max()
    if peak == 0:
        return 0.0

    idx = np.where(np.abs(mu_agg - peak) < 1e-6)[0]
    if idx.size == 0:
        return 0.0

    return (s_values[idx[0]] + s_values[idx[-1]]) * 0.5


def compute_optimal_control(T, temp_ling_var, control_ling_var, rules, steps=1001):
    s_min, s_max = get_output_range(control_ling_var)
    s_axis = np.linspace(s_min, s_max, steps)

    input_mu = fuzzify(T, temp_ling_var)
    activations = [input_mu.get(rule[0], 0.0) for rule in rules]

    mu_total = aggregate_membership(
        activations, rules, control_ling_var, s_axis
    )

    return defuzzify_mean_of_max(s_axis, mu_total)


def main(
    lvinput_path="lvinput.json",
    lvoutput_path="lvoutput.json",
    rules_path="rules.json",
    T=19.0,
):
    temp_data = json.loads(read_json_file(lvinput_path))
    control_data = json.loads(read_json_file(lvoutput_path))
    rules = json.loads(read_json_file(rules_path))

    temp_ling_var = temp_data["температура"]
    control_ling_var = control_data["нагрев"]

    return compute_optimal_control(
        T, temp_ling_var, control_ling_var, rules
    )


if __name__ == "__main__":
    result = main(T=19.0)
    print(f"Для температуры 19.0°C оптимальное управление: {result:.2f}")
