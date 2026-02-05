def analyze_items(batch_data):
    item_map = {}

    for invoice in batch_data:
        for item in invoice["items"]:
            name = item["name"]
            rate = item["rate"]

            if name not in item_map:
                item_map[name] = {
                    "min_rate": rate,
                    "max_rate": rate
                }
            else:
                item_map[name]["min_rate"] = min(item_map[name]["min_rate"], rate)
                item_map[name]["max_rate"] = max(item_map[name]["max_rate"], rate)

    item_analysis_result = []

    for name, rates in item_map.items():
        min_rate = rates["min_rate"]
        max_rate = rates["max_rate"]
        price_variance = max_rate - min_rate

        variance_flag = False
        if price_variance > (0.1 * min_rate):
            variance_flag = True

        item_analysis_result.append({
            "item": name,
            "min_rate": min_rate,
            "max_rate": max_rate,
            "price_variance": price_variance,
            "variance_flag": variance_flag
        })

    return item_analysis_result
