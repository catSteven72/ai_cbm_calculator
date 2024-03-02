import json

def convert(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    TRAIN_DATA = []
    for text, annotation in data['annotations']:
        entities = annotation['entities']
        spacy_entities = [(start, end, label) for start, end, label in entities]
        TRAIN_DATA.append((text, {"entities": spacy_entities}))

    return TRAIN_DATA
