from huffman import *

phrase = "azertyuiopdfgkm"

liste_noeuds = split_phrase_in_nodes(phrase)

while len(liste_noeuds) > 1:
    m1, m2, reste = get_two_lowest_symbols(liste_noeuds)
    m = merge_two_nodes(m1, m2)
    liste_noeuds = sort_nodes(reste + [m])

print(liste_noeuds)

res = generate_dict(liste_noeuds[0], "")
print(res)

enc = encode_phrase(phrase, res)
print(f"Encoded : {enc}, length : {len(enc)}")

enc_ascii = encode_ascii(phrase)
print(f"Pour info : {enc_ascii}, length : {len(enc_ascii)}")

print(f"Soit une compression : {round(len(enc)/ len(enc_ascii) * 100, 2)}%")