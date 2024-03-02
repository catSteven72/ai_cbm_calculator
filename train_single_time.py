from ner_annotator_converter import convert as ner_convert
import spacy
from spacy.training import Example
import random
from sklearn.model_selection import train_test_split
import model_params

def adjust_learning_rate(initial_lr, iteration, step, drop_every):
    lr = initial_lr * (step ** (iteration // drop_every))
    return lr

def update_optimizer(optimizer, new_learning_rate):
    for param_group in optimizer.param_groups:
        param_group['lr'] = new_learning_rate
    return optimizer


initial_lr, step, drop_rate, itn_num, drop_every, batch_start, batch_end, compound = model_params.get_params()

dataset = ner_convert('data/annotations_final.json')
train_data, test_data = train_test_split(dataset, test_size=0.01)

nlp = spacy.load("xx_ent_wiki_sm")

ner = nlp.get_pipe('ner')
for label in ["LENGTH", "WIDTH", "HEIGHT", "WEIGHT", "NUM_PCS", "DIM_UNITS", "WEIGHT_UNITS", "TOTAL_WEIGHT", "TOTAL_PCS", "CBM", "CW"]:
    ner.add_label(label)

other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.resume_training()

    for itn in range(itn_num):

        if itn % 10 == 0:
            learning_rate = adjust_learning_rate(initial_lr, itn, step, drop_every)
            optimizer.learn_rate = learning_rate

        random.shuffle(train_data)
        losses = {}

        batches = spacy.util.minibatch(train_data, size=spacy.util.compounding(batch_start, batch_end, compound))
        for batch in batches:
            examples = [Example.from_dict(nlp.make_doc(text), annotations) for text, annotations in batch]
            nlp.update(examples, drop=drop_rate, losses=losses, sgd=optimizer)

        print(f"Losses at iteration {itn}: {losses}")

correct_ents = 0
total_ents = 0
total_predicted_ents = 0

for text, annotations in test_data:
    doc = nlp(text)
    true_ents = annotations['entities']
    total_ents += len(true_ents)
    total_predicted_ents += len(doc.ents)

    true_set = set((ent[0], ent[1], ent[2]) for ent in true_ents)
    pred_set = set((ent.start_char, ent.end_char, ent.label_) for ent in doc.ents)

    correct_ents += len(true_set.intersection(pred_set))

precision = correct_ents / total_predicted_ents if total_predicted_ents > 0 else 0
recall = correct_ents / total_ents if total_ents > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0


nlp.to_disk("trained_model")