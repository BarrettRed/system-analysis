import json


def read_json(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json_file.read()
    return data


def parse_json_string(json_string: str) -> dict:
    data = json.loads(json_string)
    data = data['температура']
    
    values = dict()
    for value in data:
        id = value["id"]
        points = value["points"]
        values[id] = points
    
    return values


def linear_interpolation(xa, ya, xb, yb, x_val) -> float:
    if xa == xb:
        return ya
    return ya + (yb - ya) * (x_val - xa) / (xb - xa)


def calculate_trapezoidal_membership(terms, term, x) -> float:
    if term not in terms:
        return 0.0
    
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = terms[term]
    
    if x <= x1:
        return y1
    
    elif x >= x4:
        return y4
    
    elif x <= x1:
        return y1
    
    elif x >= x4:
        return y4
    
    elif x1 <= x <= x2:
        return linear_interpolation(x1, y1, x2, y2, x)
    
    elif x2 <= x <= x3:
        return linear_interpolation(x2, y2, x3, y3, x)
    
    elif x3 <= x <= x4:
        return linear_interpolation(x3, y3, x4, y4, x)
    
    else:
        return 0.0


def create_output_range(terms_dict):
    all_points = []
    for points in terms_dict.values():
        for x, _ in points:
            all_points.append(x)
    return min(all_points), max(all_points)


def generate_discrete_values(s_min, s_max, num_points=1000):
    return [
        s_min + i * (s_max - s_min) / (num_points - 1)
        for i in range(num_points)
    ]


def load_input_data(temperature_json: str, heat_lvl_json: str, mapping_json: str):
    """Загрузка и парсинг всех входных данных"""
    temperature_terms = parse_json_string(temperature_json)
    heat_lvl_terms = parse_json_string(heat_lvl_json)
    mapping = json.loads(mapping_json)
    
    return temperature_terms, heat_lvl_terms, mapping


def apply_fuzzy_rules(temperature_terms, heat_lvl_terms, mapping, current_temp, s_values):
    aggregated_membership = [0.0] * len(s_values)
    
    for rule in mapping:
        temp_term, heat_term = rule[0], rule[1]
        activation = calculate_trapezoidal_membership(temperature_terms, temp_term, current_temp)
        
        if activation > 0:
            for i, s in enumerate(s_values):
                mu_heat_lvl = calculate_trapezoidal_membership(heat_lvl_terms, heat_term, s)
                aggregated_membership[i] = max(
                    aggregated_membership[i], 
                    min(activation, mu_heat_lvl)
                )
    
    return aggregated_membership


def defuzzify(aggregated_membership, s_values, s_min, s_max):
    peak_membership = max(aggregated_membership)
    
    if peak_membership == 0:
        return (s_min + s_max) / 2
    
    for i, mu in enumerate(aggregated_membership):
        if mu == peak_membership:
            return s_values[i]
    
    return s_values[0]


def main(temperature_json: str, heat_lvl_json: str, mapping_json: str, current_temp: float) -> float:
    temperature_terms = parse_json_string(temperature_json)
    heat_lvl_terms = parse_json_string(heat_lvl_json)
    mapping = json.loads(mapping_json)
    
    s_min, s_max = create_output_range(heat_lvl_terms)
    s_values = generate_discrete_values(s_min, s_max)
    
    aggregated_membership = apply_fuzzy_rules(temperature_terms, heat_lvl_terms, mapping, current_temp, s_values)
    
    control_value = defuzzify(aggregated_membership, s_values, s_min, s_max)
    
    return control_value



if __name__ == "__main__":
    temperature_json: str = read_json("task4/temperature.json")
    heat_lvl_json: str = read_json("task4/heat_lvl.json")
    mapping_json: str = read_json("task4/mapping.json")

    current_temperature = 23.0
    control_value: float  = main(temperature_json, heat_lvl_json, mapping_json, current_temperature)

    print(f"Значение оптимального управления = {control_value} для температуры: {current_temperature}")