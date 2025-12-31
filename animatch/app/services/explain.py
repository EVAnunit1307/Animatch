feature_labels = {"face_ratio": "Close face proportions",
    "eye_spacing": "Similar eye spacing",
    "eye_openness": "Similar eye openness",
    "jaw_angle": "Comparable jaw geometry",
    "chin_ratio": "Similar chin width",
    "brow_height": "Similar brow height"
} # temp definition before langchain 


def explain_match(user_vector:float, char_vector:float , max_response = 3):
    differences = []
    for key in user_vector:
        # abs makes it positive so we only get [(0.01, "eye_spacing"), ...]
        differences.append((abs(user_vector[key] - char_vector[key]), key))

    # Sort by smallest difference first
    differences.sort(key=lambda x: x[0])

    reasons = []
    for _, key in differences[:max_response]:
        reasons.append(feature_labels.get(key, f"Similar {key}"))

    return reasons

        
