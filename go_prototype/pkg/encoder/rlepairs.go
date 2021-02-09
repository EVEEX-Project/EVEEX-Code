package encoder

import "strconv"

// RLEPair contains the data associated
// to a RLE pair
type RLEPair struct {
	NbZeros int
	Value float64
}

// ToString returns the representation of the pair
// useful for huffman for example
func (p *RLEPair) ToString() string {
	sNbZeros := strconv.FormatInt(int64(p.NbZeros), 10)
	sValue := strconv.FormatFloat(p.Value, 'd', 2, 64)
	return sNbZeros + ";" + sValue
}
