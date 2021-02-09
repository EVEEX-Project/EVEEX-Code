package huffman

import (
	"fmt"
	"testing"
)

func TestHuffman(t *testing.T) {
	phrase := "le chic a l'ensta breton"
	nodeList := SplitPhraseInNodes(phrase)

	for _, node := range nodeList {
		node.PrintNode()
	}

	root := GenerateTreeFromList(nodeList)

	symbols := make(map[string]string)
	GenerateEncodingDict(&symbols, root,"")

	PrintTree(root)

	for key, val := range symbols {
		fmt.Printf("%s --> %s\n", key, val)
	}
}