class Noeud:

    def __init__(self, valeur, frequence, gauche=None, droite=None):
        self.frequence = frequence
        self.valeur = valeur
        self.droite = droite
        self.gauche = gauche

    def __repr__(self):
        return f"Fréquence : {self.frequence}, Valeur = {self.valeur}"

    def display(self):
        lines, *_ = self.display_aux()
        for l in lines:
            print(l)

    def display_aux(self):
        if self.droite is None and self.gauche is None:
            line = f"{self.valeur}"
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        if self.droite is None:
            lines, n, p, x = self.gauche.display_aux()
            s = f"{self.valeur}"
            u = len(s)
            first_line = (x + 1) * " " + (n - x - 1) * "_" + s
            second_line = x * " " + (n - x - 1 + u) * " "
            shifted_lines = [line + u * " " for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u//2

        if self.gauche is None:
            lines, n, p, x = self.droite.display_aux()
            s = f"{self.valeur}"
            u = len(s)
            first_line = s + x * "_" + (n - x) * " "
            second_line = (u + x) * " " + "\\" + (n - x - 1) * " "
            shifted_lines = [u * " " + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        left, n, p, x = self.gauche.display_aux()
        right, m, q, y = self.droite.display_aux()
        s =  f"[0 1]"
        u = len(s)
        first_line = (x + 1) * " " + (n - x - 1) * "_" + s + y * "_" + (m - y) * " "
        second_line = x * " " + "/" + (n - x - 1 + u + y) * " " + "\\" + (m - y - 1) * " "
        if p < q:
            left += [n * " "] * (q - p)
        elif q < p:
            right += [m * " "] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * " " + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u//2


class Huffman:

    def __init__(self, phrase):
        self.noeuds = []
        self.symbols = {}
        self.phrase = phrase

        self.split_phrase_in_nodes(self.phrase)

    def split_phrase_in_nodes(self, phrase):
        self.symbols = {}
        self.noeuds = []
        for c in phrase:
            if c in self.symbols:
                self.symbols[c] += 1
            else:
                self.symbols[c] = 1

        for key in self.symbols:
            self.noeuds.append(Noeud(key, self.symbols[key]))

        return self.noeuds

    def merge_two_nodes(self, noeud_a, noeud_b):
        return Noeud([noeud_a.valeur, noeud_b.valeur], noeud_a.frequence + noeud_b.frequence, noeud_a, noeud_b)

    def get_two_lowest_symbols(self):
        def get_score(noeud):
            return noeud.frequence

        tmp = self.noeuds[:]

        min1 = min(tmp, key=get_score)
        tmp.remove(min1)

        min2 = min(tmp, key=get_score)
        tmp.remove(min2)

        return min1, min2, tmp

    def sort_nodes(self, liste_noeuds = None):
        if liste_noeuds != None:
            return sorted(liste_noeuds, key=lambda x:x.frequence, reverse=True)
        else:
            self.noeuds = sorted(self.noeuds, key=lambda x:x.frequence, reverse=True)

    def generate_dict(self, racine, prefixe=""):
        if racine.gauche is None and racine.droite is None:
            return {racine.valeur: prefixe}

        res = {}
        if racine.gauche is not None:
            res.update(self.generate_dict(racine.gauche, prefixe + "0"))
        if racine.droite is not None:
            res.update(self.generate_dict(racine.droite, prefixe + "1"))
        return res

    @staticmethod
    def reverse_dict(entry_dict):
        res = {}
        for key in entry_dict:
            res[entry_dict[key]] = key
        return res

    def encode_phrase(self, phrase = None, dictionnary = None):
        res = ""

        if phrase is None:
            phrase = self.phrase

        for l in phrase:
            if dictionnary is not None:
                res += dictionnary[l]
            else:
                res += self.symbols[l]
        return res

    @staticmethod
    def encode_ascii(phrase):
        res = ""
        for l in phrase:
            res += str(bin(ord(l))[2:])
        return res

    def decode_phrase(self, enc, dico = None):
        buffer = ""
        res = ""
        if dico is not None:
            dico = self.reverse_dict(dico)
        else:
            dico = self.reverse_dict(self.symbols)
        for l in enc:
            buffer += l
            if buffer in dico:
                res += dico[buffer]
                buffer = ""
        return res