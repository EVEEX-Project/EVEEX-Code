class Noeud:

    def __init__(self, valeur, frequence, gauche=None, droite=None):
        self.frequence = frequence
        self.valeur = valeur
        self.droite = droite
        self.gauche = gauche

    def __repr__(self):
        return f"Fréquence : {self.frequence}, Valeur = {self.valeur}"


def split_phrase_in_nodes(phrase):
    symbols = {}
    for c in phrase:
        if c in symbols:
            symbols[c] += 1
        else:
            symbols[c] = 1
    noeuds = []
    for key in symbols:
        noeuds.append(Noeud(key, symbols[key]))

    return noeuds


def merge_two_nodes(noeud_a, noeud_b):
    return Noeud([noeud_a.valeur, noeud_b.valeur], noeud_a.frequence + noeud_b.frequence, noeud_a, noeud_b)


def get_two_lowest_symbols(liste_noeuds):
    def get_score(noeud):
        return noeud.frequence
    tmp = liste_noeuds[:]

    min1 = min(tmp, key=get_score)
    tmp.remove(min1)

    min2 = min(tmp, key=get_score)
    tmp.remove(min2)

    return min1, min2, tmp


def sort_nodes(liste_noeuds):
    return sorted(liste_noeuds, key=lambda x:x.frequence, reverse=True)


def generate_dict():
    pass