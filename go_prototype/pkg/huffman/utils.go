package huffman

import (
	"github.com/rs/zerolog/log"
)

// PrintNode prints in the console the representation of a node
func (n* Node) PrintNode() {
	log.Debug().
		Int("frequency", n.frequency).
		Str("value", n.value[0]).
		Msg("Node -> ")
}

// removeFromList is a fast implementation of a way
// to remove an element from a list from its idx
func removeFromList(list []*Node, idx int) []*Node {
	var res []*Node
	res = append(res, list[:idx]...)
	res = append(res, list[idx+1:]...)
	return res
}
