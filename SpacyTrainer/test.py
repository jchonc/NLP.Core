
#!/usr/bin/env python3
# coding: utf8
"""Traning from existing incident data
"""
from __future__ import unicode_literals, print_function
import json

import random
from pathlib import Path
import thinc.extra.datasets

import spacy
from spacy.util import minibatch, compounding

def main():

    output_dir="model" 
    n_iter = 7
    nlp = spacy.load("en_core_web_sm")  # load existing spaCy model
    print("Loaded model")

    # add the text classifier to the pipeline if it doesn't exist
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'textcat' not in nlp.pipe_names:
        textcat = nlp.create_pipe('textcat')
        nlp.add_pipe(textcat)
    # otherwise, get it, so we can add labels to it
    else:
        textcat = nlp.get_pipe('textcat')

    if 'ner' not in nlp.pipe_names: 
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)
    else:
        ner = nlp.get_pipe('ner')

    # add label to text classifier

    knownTags = [
        "Employee Event",
        "Severity 2 Temporary/Minor Harm to Patient/Employee/Visitor/Property",
        "Feedback",
        "Diagnosis/Treatment Issue",
        "Medication Error",
        "Severity 1 Reached but no Harm to Patient/Employee/Visitor/Property",
        "Fall Event",
        "Lab/Specimen Test",
        "Provision of Care",
        "Severity 0 Near Miss Event",
        "Facilities",
        "Safety/Security Event",
        "IV/Vascular Access Device",
        "Surgery/Procedure",
        "Diagnostic Imaging Event",
        "Severity 3 Major/Permanent Harm to Patient/Employee/Visitor/Property",
        "Skin/Tissue",
        "Airway Management",
        "Adverse Drug Reaction",
        "Not Administered",
        "Maternal/Childbirth",
        "Line/Tube",
        "Patient ID/Documentation/Consent",
        "Unexpected Medical Event",
        "Infection Event",
        "Restraint Event",
        "Blood/Blood Product",
        "Severity 4 Death/Catastrophic Event",
        "Not Charted",
        "Emergency Code",
        "Not Performed"
    ]
    for tag in knownTags:
        textcat.add_label(tag)    

    print("Loading training data...")
    data = json.load(open('c:\\backup\\DataNv1.json', encoding='utf8'))

    all_data = []
    for d in data:
        git = d['GeneralIncidentType']
        severity = d['Severity']
        cats = {tag: ( tag==git ) or ( tag == severity ) for tag in knownTags}
        all_data.append((d['Description'], {'cats':cats}))
    print("Load {} incidents".format(len(all_data)))

    training_data = all_data[:-2000]
    test_data = all_data[-1000:-1]

    print("Using {} as training data, {} as test data)"
          .format(len(training_data), len(test_data)))

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']
    with nlp.disable_pipes(*other_pipes):  # only train textcat
        optimizer = nlp.begin_training()
        print("Training the model...")
        print('{:^5}\t{:^5}\t{:^5}\t{:^5}'.format('LOSS', 'P', 'R', 'F'))
        for _ in range(n_iter):
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(training_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.2,
                           losses=losses)
            with textcat.model.use_params(optimizer.averages):
                scores = evaluate(nlp.tokenizer, textcat, test_data)
            print('{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}'  # print a simple table
                  .format(losses['textcat'], scores['textcat_p'],
                          scores['textcat_r'], scores['textcat_f']))

    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

def evaluate(tokenizer, textcat, test_data):
    (texts, cats) = zip(*test_data)
    docs = (tokenizer(text) for text in texts)
    tp = 1e-8  # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 1e-8  # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]['cats']
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if score >= 0.5 and gold[label]:
                tp += 1.
            elif score >= 0.5 and (not gold[label]):
                fp += 1.
            elif score < 0.5 and gold[label]:
                tn += 1
            elif score < 0.5 and (not gold[label]):
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f_score = 2 * (precision * recall) / (precision + recall)
    return {'textcat_p': precision, 'textcat_r': recall, 'textcat_f': f_score}


if __name__ == '__main__':
    exit(main())