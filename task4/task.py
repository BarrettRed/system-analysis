import json


def read_json(file_path: str) -> str:
    buffer = []
    with open(file_path, 'r', encoding='utf-8') as fh:
        while chunk := fh.read(4096):
            buffer.append(chunk)
    return ''.join(buffer)


def parse_json_string(json_string: str) -> dict:
    payload = json.loads(json_string)
    records = payload.get('температура', [])
    
    result = {}
    for entry in records:
        key = entry["id"]
        coords = entry["points"]
        result[key] = coords
    
    return result


def linear_interpolation(xa, ya, xb, yb, x_val) -> float:
    dx = xb - xa
    if abs(dx) < 1e-9:
        return ya
    t = (x_val - xa) / dx
    return ya + (yb - ya) * t


def calculate_trapezoidal_membership(terms, term, x) -> float:
    if term not in terms:
        return 0.0
    
    pts = terms[term]
    (a, ha), (b, hb), (c, hc), (d, hd) = pts
    
    if x < a:
        return ha if x <= a else 0.0
    
    if x > d:
        return hd if x >= d else 0.0
    
    if a <= x <= b:
        if abs(b - a) < 1e-9:
            return max(ha, hb)
        return linear_interpolation(a, ha, b, hb, x)
    
    if b <= x <= c:
        return max(hb, hc)
    
    if c <= x <= d:
        if abs(d - c) < 1e-9:
            return max(hc, hd)
        return linear_interpolation(c, hc, d, hd, x)
    
    return 0.0


def create_output_range(terms_dict):
    extremes = []
    for _, shape in terms_dict.items():
        for coord, _ in shape:
            extremes.append(coord)
    return (min(extremes), max(extremes)) if extremes else (0, 1)


def generate_discrete_values(s_min, s_max, num_points=1000):
    step = (s_max - s_min) / (num_points - 1) if num_points > 1 else 0
    return [s_min + idx * step for idx in range(num_points)]


def load_input_data(temperature_json: str, heat_lvl_json: str, mapping_json: str):
    temp_data = parse_json_string(temperature_json)
    heat_data = parse_json_string(heat_lvl_json)
    rules = json.loads(mapping_json)
    
    return temp_data, heat_data, rules


def apply_fuzzy_rules(temperature_terms, heat_lvl_terms, mapping, current_temp, s_values):
    n = len(s_values)
    accumulator = [0.0 for _ in range(n)]
    
    for condition, consequence in mapping:
        firing_strength = calculate_trapezoidal_membership(temperature_terms, condition, current_temp)
        
        if firing_strength <= 0:
            continue
            
        for idx, s_coord in enumerate(s_values):
            degree = calculate_trapezoidal_membership(heat_lvl_terms, consequence, s_coord)
            clipped = firing_strength if firing_strength < degree else degree
            if clipped > accumulator[idx]:
                accumulator[idx] = clipped
    
    return accumulator


def defuzzify(aggregated_membership, s_values, s_min, s_max):
    top_val = max(aggregated_membership) if aggregated_membership else 0.0
    
    if top_val == 0:
        return (s_min + s_max) * 0.5
    
    candidates = [s_values[i] for i, val in enumerate(aggregated_membership) if val == top_val]
    return candidates[len(candidates) // 2] if candidates else s_values[0]


def main(temperature_json: str, heat_lvl_json: str, mapping_json: str, current_temp: float) -> float:
    input_vars = parse_json_string(temperature_json)
    output_vars = parse_json_string(heat_lvl_json)
    rule_base = json.loads(mapping_json)
    
    lower, upper = create_output_range(output_vars)
    universe = generate_discrete_values(lower, upper)
    
    fuzzy_output = apply_fuzzy_rules(input_vars, output_vars, rule_base, current_temp, universe)
    
    crisp_value = defuzzify(fuzzy_output, universe, lower, upper)
    
    return crisp_value



if __name__ == "__main__":
    temperature_json: str = read_json("task4/temperature.json")
    heat_lvl_json: str = read_json("task4/heat_lvl.json")
    mapping_json: str = read_json("task4/mapping.json")

    current_temperature = 23.0
    control_value: float = main(temperature_json, heat_lvl_json, mapping_json, current_temperature)

    print(f"Значение оптимального управления = {control_value} для температуры: {current_temperature}")