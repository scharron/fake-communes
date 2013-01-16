Fake-Commune
============

A French commune name generator.


    python fake_commune.py 10

will generate 10 fake commune names

    Poules-Saint-Quen-Reynos-Alban-des-et-Laurecourbelins 
    Saint-Jean-Germolasvillapocolenargues
    Bénérachères
    Oricourges
    Lant-Genès 
    La Tour-du-Valon
    Andebourt-Lamanville
    Veslairettnaulxures-Arraiges
    Issilleneuve-d'Oléray
    Saint-Cyr-des Istre-du-Royalet-Montrac-Caponciennebucource 


You can configure the ngrams length using `--ngram N`. A greater value is more realistic but less inventive.

    python3 fake_commune.py --ngram 2 3

    Camont-Orvandrésin
    Appelle-et
    Épial-dene

    python3 fake_commune.py --ngram 5 3

    Brueil-Mousson
    Sainte-Marie
    Sons-en-Auxonne
