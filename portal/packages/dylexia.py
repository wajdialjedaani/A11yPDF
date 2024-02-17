

def analyze_dylexia(fonts_dict):
    readable_fonts = [
        'Arial', 'Comic Sans', 'Verdana', 'Tahoma',
        'Century Gothic', 'Trebuchet', 'Calibri', 'Open Sans'
    ]

    matching_fonts = {font: count for font, count in fonts_dict.items() if any(rf in font for rf in readable_fonts)}

    non_matching_fonts = {font: count for font, count in fonts_dict.items() if not any(rf in font for rf in readable_fonts)}

    total_usage = sum(fonts_dict.values())

    # Calculate the total usage of readable (matching) fonts
    matching_usage = sum(matching_fonts.values())

    # Calculate the overall percentage of usage for readable fonts
    percentage = (matching_usage / total_usage) * 100
    return percentage,matching_fonts,non_matching_fonts