import json

size = 3


def get_communes(out):
    """
    Get the list of communes from dbpedia.
    """
    import requests
    import urllib.parse

    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    CONSTRUCT {
        ?commune rdfs:label ?name .
    }
    WHERE {
        ?commune a dbo:Settlement ;
        dbo:country dbr:France ;
        rdfs:label ?name .
        FILTER (LANG(?name) = 'fr') .
    }
    """

    url = "http://dbpedia.org/sparql?output=JSON&query=%s"
    url = url % urllib.parse.quote_plus(query)

    out("> Downloading commune file")
    out("> Querying dbpedia")
    out("> Please wait...")

    res = requests.get(url)

    out("> Done!")

    if res.status_code != 200:
        raise IOError("Unable to get the communes list")

    return res.json()


def learn(communes, size=3):
    import collections
    import re

    def clean(c):
        return re.sub("\([^(]*\)", "", c)

    communes = [clean(commune) for commune in communes]

    ngram = lambda: collections.defaultdict(lambda: 0)
    ngrams = collections.defaultdict(ngram)

    for commune in communes:
        l = len(commune)
        if l < size:
            continue

        # Start symbol
        prev = "^"

        for i in range(0, l - size + 1):
            ngram = commune[i:i + size]

            ngrams[prev][ngram] += 1
            prev = ngram

        ngrams[prev]["$"] += 1

    model = {}
    for ngram, transitions in ngrams.items():
        model[ngram] = []
        total = sum(transitions.values())
        for other, count in transitions.items():
            model[ngram].append((count / total, other))

    return model


def gen(model):
    import random

    def select(transition, select):
        choice = 0
        for proba, ngram in transition:
            if choice + proba > select:
                return ngram
            choice += proba

    output = ""
    prev = "^"

    while True:
        v = random.random()
        next = select(model[prev], v)
        if next == "$":
            return output
        if prev == "^":
            output = next
        else:
            output += next[-1]
        prev = next


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Generate fake communes names")

    parser.add_argument("--dont-save-communes",
                        dest="save_communes",
                        action="store_false",
                        default=True,
                        help="Don't save the list of communes "
                             "(download, use, and trash)")

    parser.add_argument("--dont-save-model",
                        dest="save_model",
                        action="store_false",
                        default=True,
                        help="Don't save the model of learnt elements"
                             "(generate, use, and trash)")

    parser.add_argument("--ngram",
                        type=int,
                        metavar="SIZE",
                        dest="ngram",
                        action="store",
                        default=3,
                        help="ngram length"
                             "greater is more true, but less inventive")

    parser.add_argument("n",
                        metavar="N",
                        type=int,
                        nargs=1,
                        help="number of fake names to generate")

    parser.add_argument("-v", "--verbose",
                        dest="verbose",
                        action="store_true",
                        default=False,
                        help="Say things")

    args = parser.parse_args()

    def ignore(*args):
        pass
    out = print if args.verbose else ignore

    out("Loading communes file...")
    try:
        communes = json.load(open("communes.json"))["results"]["bindings"]
        communes = [commune["o"]["value"] for commune in communes]
    except IOError:
        communes = get_communes(out)
        if args.save_communes:
            json.dump(communes, open("communes.json", "w"), indent=2)
    out("Done!")

    out("Loading model file...")
    try:
        model = json.load(open("communes.model.json"))
    except IOError:
        model = {}

    if args.ngram not in model:
        model[args.ngram] = learn(communes, args.ngram)
        if args.save_model:
            json.dump(model, open("communes.model.json", "w"), indent=2)
    model = model[args.ngram]
    out("Done!")

    out("Generating %i fake commune names" % args.n[0])
    for i in range(args.n[0]):
        print(gen(model))
