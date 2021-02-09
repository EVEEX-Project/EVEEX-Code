package huffman

import "fmt"

func (n* Node) PrintNode() {
	fmt.Printf("-- Fréquence : %d, Value : %s\n", n.frequency, n.value[0])
}

func removeFromList(list []*Node, idx int) []*Node {
	var res []*Node
	res = append(res, list[:idx]...)
	res = append(res, list[idx+1:]...)
	return res
}
