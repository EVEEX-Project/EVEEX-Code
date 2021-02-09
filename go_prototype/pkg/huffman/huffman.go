package huffman

import (
	"eveex/pkg/encoder"
	"math"
)

// Node contains data about a node
// for the Huffman encoding algorithm
type Node struct {
	value []string
	frequency int
	right *Node
	left *Node
}

// MergeTwoNodes takes to nodes and merges it into another one
// while updating their frequency and their value
func MergeTwoNodes(a *Node, b *Node) *Node {
	var res Node

	// Adding every element to the new value
	res.value = append(res.value, a.value...)
	res.value = append(res.value, b.value...)

	// Updating frequency
	res.frequency = a.frequency + b.frequency

	// Updating node links
	res.left = a
	res.right = b

	return &res
}

// SplitPhraseInNodes takes a sentence (made of words) and
// splits it into nodes with a frequency
func SplitPhraseInNodes(phrase string) []*Node {
	var nodeList []*Node
	var symbols = make(map[string]int)

	for k := 0; k < len([]rune(phrase)); k ++ {
		key := string([]rune(phrase)[k])

		freq := 0
		if val, ok := symbols[key]; ok {
			// if the key is already registered
			freq = val
		}
		// Updating the frequency
		symbols[key] = freq + 1
	}

	for symbol, freq := range symbols {
		nodeList = append(nodeList, &Node{
			value: []string{symbol},
			frequency: freq,
		})
	}

	return nodeList
}

// RLEPairsToNodes takes a list of pairs and
// splits it into nodes with a frequency
func RLEPairsToNodes(pairs []encoder.RLEPair) []*Node {
	var nodeList []*Node
	symbols := make(map[string]int)

	for _, pair := range pairs {
		key := pair.ToString()

		freq := 0
		if val, ok := symbols[key]; ok {
			// if the key is already registered
			freq = val
		}
		// Updating the frequency
		symbols[key] = freq + 1
	}

	for symbol, freq := range symbols {
		nodeList = append(nodeList, &Node{
			value: []string{symbol},
			frequency: freq,
		})
	}

	return nodeList
}

// GetLowestFrequencySymbol returns the node from the list
// with the lowest frequency
func GetLowestFrequencySymbol(nodeList []*Node) (int, *Node) {
	var lowestNode *Node
	idx := -1
	minFreq := math.Inf(1)

	for k, node := range nodeList {
		if float64(node.frequency) < minFreq {
			if lowestNode == nil || len(lowestNode.value) < len(node.value) {
				idx = k
				minFreq = float64(node.frequency)
				lowestNode = node
			}
		}
	}

	return idx, lowestNode
}

// GenerateTreeFromList generates a tree from a list of nodes
// then returns the root of the tree
func GenerateTreeFromList(nodeList []*Node) *Node {
	var n1, n2, n12 *Node
	var idx int

	for len(nodeList) > 1 {
		idx, n1 = GetLowestFrequencySymbol(nodeList)
		nodeList = removeFromList(nodeList, idx)
		idx, n2 = GetLowestFrequencySymbol(nodeList)
		nodeList = removeFromList(nodeList, idx)

		n12 = MergeTwoNodes(n1, n2)
		nodeList = append(nodeList, n12)
	}

	return nodeList[0]
}

// GenerateEncodingDict takes a dictionary and a node and
// fills the dictionary with the corresponding symbols and
// encoding bytes
func GenerateEncodingDict(dictionary *map[string]string, root *Node, prefix string) {

	// if there is no children we add the symbol to the dictionary
	if root.left == nil && root.right == nil {
		(*dictionary)[root.value[0]] = prefix
	}

	if root.left != nil {
		GenerateEncodingDict(dictionary, root.left, prefix + "0")
	}
	if root.right != nil {
		GenerateEncodingDict(dictionary, root.right, prefix + "1")
	}
}

