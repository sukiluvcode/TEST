import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("It is shown that Sr2B5O9(OH)·H2O is a direct gap compound with a calculated band gap of 5.56 eV")
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_,
            chunk.root.head.text)
