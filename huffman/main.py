from huffman import *

phrase = "CITRONTRESCONTENT"

liste_noeuds = split_phrase_in_nodes(phrase)

while len(liste_noeuds) > 1:
    m1, m2, reste = get_two_lowest_symbols(liste_noeuds)
    m = merge_two_nodes(m1, m2)
    liste_noeuds = sort_nodes(reste + [m])

print(liste_noeuds)

res = generate_dict(liste_noeuds[0], "")
print(res)