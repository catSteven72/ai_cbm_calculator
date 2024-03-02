import json
import re
import os

def get_file_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def preprocess_user_input(input_string):
    lines = input_string.split('\n')

    # Add a space between a letter followed by a period and a digit
    processed_lines = [re.sub(r'(?<=\D\.)\s*(?=\d)', r' ', line) for line in lines]

    # Add a space between a non-digit character and a following digit, but ignore decimal points
    processed_lines = [re.sub(r'(?<=[^\d\s.,])(?=\d)', r' ', line) for line in processed_lines]

    # Add a space between a non-digit character and a preceding digit, but ignore decimal points
    processed_lines = [
        re.sub(r'(?<=\d)(?=[^\d\s.,])', r' ', line) for line in processed_lines
    ]

    # Add spaces around '/', '\', '-', ';', 'x', 'х', '*', '@', '+', '(', and ')' in appropriate contexts
    processed_lines = [re.sub(r'(?<=\d)\s*([xXхХ])\s*(?=\d)', r' \1 ', line) for line in processed_lines]
    processed_lines = [
        re.sub(r'(?<!\s)@\s*(?=\S)|(?<=\S)\s*@(?!\s)', r' @ ', line)
        for line in processed_lines
    ]
    processed_lines = [re.sub(r'(?<=\d)\s*(\()|(\))\s*(?=\d)|\s*(\()|\s*(\))', r' \1\2\3\4 ', line) for line in processed_lines]


    processed_lines = [re.sub(r'([()])\s*(?=\d)', r'\1 ', line) for line in processed_lines]
    processed_lines = [
        re.sub(r'(?<!\s)\*\s*(?=\S)|(?<=\S)\s*\*(?!\s)', r' * ', line)
        for line in processed_lines
    ]
    processed_lines = [
        re.sub(r'(?<!\s);\s*(?=\S)|(?<=\S)\s*;(?!\s)', r' ; ', line)
        for line in processed_lines
    ]
    processed_lines = [
        re.sub(r'(?<!\s)/\s*(?=\S)|(?<=\S)\s*/(?!\s)', r' / ', line)
        for line in processed_lines
    ]
    processed_lines = [
        re.sub(r'(?<!\s)\\\s*(?=\S)|(?<=\S)\s*\\(?!\s)', r' \ ', line)
        for line in processed_lines
    ]
    processed_lines = [
        re.sub(r'(?<!\s)-\s*(?=\S)|(?<=\S)\s*-(?!\s)', r' - ', line)
        for line in processed_lines
    ]
    processed_lines = [
        re.sub(r'(?<!\s)\+\s*(?=\S)|(?<=\S)\s*\+(?!\s)', r' + ', line)
        for line in processed_lines
    ]

    # Removes extra space between 'm' and '3' when indicating cubic meters
    processed_lines = [re.sub(r'(?i)(\s+m)\s+(3)', r'\1\2', line) for line in processed_lines]

    # Add space around 'h' when used between digits
    processed_lines = [re.sub(r'(?<=\d)h(?=\d)', r' h ', line, flags=re.I) for line in processed_lines]

    # Adds spaces around commas and periods unless part of a decimal number
    processed_lines = [
        re.sub(r'(?<=[^\s\d])[,.，](?=[^\s])|(?<=[^\s])[,.，](?=[^\s\d])', r' \g<0> ', line)
        for line in processed_lines
    ]

    # Add space before units if they directly follow a number without space, handling 'm3' specifically
    processed_lines = [
        re.sub(
            r'(\d)(c\.w\.|cw|pll|box|crtns|ctns|cmb|cbm|ct|pc|pcs|kgs|lbs|kg|ccm|cmm|cms|m|cm|mm|in|vnt|ton|tonn|tones|кг|см|м|дюйм|дюймы|дюймов|kg\.|cm\.|mm\.|inches|m(?!\d))',
            r'\1 \2', line, flags=re.I)
        for line in processed_lines]

    # Add spaces around '='
    processed_lines = [re.sub(r'(?<!=)([=])(?!=)', r' = ', line) for line in processed_lines]

    # Add a space before "." when preceded by letters and not part of decimal numbers
    processed_lines = [
        re.sub(r'(?<=[a-zA-Z])(\.)\s*(?=\d|\s*[a-zA-Z])', r' \1 ', line)
        for line in processed_lines
    ]

    # Correct potential double spaces
    processed_lines = [re.sub(r'\s{2,}', ' ', line) for line in processed_lines]

    return '\n'.join(processed_lines)

def preprocess_file(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        contents = file.read()

    processed_contents = preprocess_user_input(contents)

    file_name = get_file_name(file_path)
    new_file_name = file_name + " processed.txt"

    with open(f"data/{new_file_name}", 'w', encoding='utf-8') as file:
        file.write(processed_contents)

def comma_to_period(text_with_commas):
    text_with_periods = text_with_commas.replace(',', '.')
    return text_with_periods
