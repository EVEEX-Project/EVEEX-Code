import huffman

phrase = "J’ai un python qui marche ( j’ai installé un environnement python virtuel )"

liste_noeuds = huffman.split_phrase_in_nodes(phrase)

while len(liste_noeuds) > 1:
    m1, m2, reste = huffman.get_two_lowest_symbols(liste_noeuds)
    m = huffman.merge_two_nodes(m1, m2)
    liste_noeuds = huffman.sort_nodes(reste + [m])

# On affiche l'arbre construit
liste_noeuds[0].display()

# On génère le dictionnaire en parcourant l'arbre
enc_dico = huffman.generate_dict(liste_noeuds[0], "")
print(f"Dictionnaire d'encodage : {enc_dico}")

# On encode le message avec le dictionnaire
enc = huffman.encode_phrase(phrase, enc_dico)
print(f"Encoded : {enc}, length : {len(enc)}")

enc_ascii = huffman.encode_ascii(phrase)
print(f"Pour info : {enc_ascii}, length : {len(enc_ascii)}")

print(f"Soit une compression : {round(len(enc)/ len(enc_ascii) * 100, 2)}%")

print(f"Message décodé : {huffman.decode_phrase(enc, enc_dico)}")