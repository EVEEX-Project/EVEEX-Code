package huffman

import (
	"eveex/pkg/encoder"
	"testing"
)

func assertEqual(t *testing.T, variable interface{}, expected interface{}) {
	if variable != expected {
		t.Errorf("AssertEqual mismatch - Expected: %+v, Got: %+v\n", expected, variable)
	}
}

func assertNotEqual(t *testing.T, variable interface{}, notExpected interface{}) {
	if variable == notExpected {
		t.Errorf("AssertNotEqual mismatch - Not wanted: %+v, Got: %+v\n", notExpected, variable)
	}
}

func TestInitNode(t *testing.T) {
	n1 := Node{
		value:     []string{"a"},
		frequency: 1,
	}

	assertEqual(t, n1.frequency, 1)
	assertEqual(t, len(n1.value), 1)
	assertEqual(t, n1.value[0], "a")
}

func TestMergeNodes(t *testing.T) {
	n1 := &Node{
		value:     []string{"a"},
		frequency: 1,
	}

	n2 := &Node{
		value:     []string{"b"},
		frequency: 5,
	}

	n12 := MergeTwoNodes(n1, n2)

	assertEqual(t, n12.frequency, n1.frequency + n2.frequency)
	assertEqual(t, len(n12.value), len(n1.value) + len(n2.value))
	assertEqual(t, n12.left, n1)
	assertEqual(t, n12.right, n2)
}

func TestSplitPhraseInNodes(t *testing.T) {
	phrase := "hello"
	nodes := SplitPhraseInNodes(phrase)

	assertEqual(t, len(nodes), 4)

	var sum int
	for _, node := range nodes {
		sum += node.frequency
	}
	assertEqual(t, sum, len(phrase))
}

func TestGetLowestFrequencySymbol(t *testing.T) {
	phrase := "hello"
	nodes := SplitPhraseInNodes(phrase)

	_, low := GetLowestFrequencySymbol(nodes)
	assertEqual(t, low.frequency, 1)
}

func TestGenerateTreeFromList(t *testing.T) {
	phrase := "hello"
	nodes := SplitPhraseInNodes(phrase)

	tree := GenerateTreeFromList(nodes)

	assertEqual(t, tree.frequency, len(phrase))
	assertNotEqual(t, tree.right, nil)
	assertNotEqual(t, tree.left, nil)
}

func TestGenerateEncodingDict(t *testing.T) {
	phrase := "hello"
	nodes := SplitPhraseInNodes(phrase)
	tree := GenerateTreeFromList(nodes)

	var symbols = map[string]string{}
	GenerateEncodingDict(&symbols, tree, "")

	assertEqual(t, len(symbols), 4)
	assertNotEqual(t, symbols["h"], "")
}

func TestRLEPairsToNodes(t *testing.T) {
	pairs := []encoder.RLEPair{
		encoder.RLEPair{
			NbZeros: 0,
			Value:   5,
		},
		encoder.RLEPair{
			NbZeros: 140,
			Value:   4.5,
		},
		encoder.RLEPair{
			NbZeros: 0,
			Value:   5,
		},
	}

	nodes := RLEPairsToNodes(pairs)
	assertEqual(t, len(nodes), 2)

	_, low := GetLowestFrequencySymbol(nodes)
	assertEqual(t, low.frequency, 1)
}

func TestPrintNode(t *testing.T) {
	n1 := Node{
		value:     []string{"a"},
		frequency: 5,
	}
	// visual test
	n1.PrintNode()
}

func TestPrintTree(t *testing.T) {
	phrase := "hello world"
	nodes := SplitPhraseInNodes(phrase)
	tree := GenerateTreeFromList(nodes)

	// visual test
	PrintTree(tree)
}