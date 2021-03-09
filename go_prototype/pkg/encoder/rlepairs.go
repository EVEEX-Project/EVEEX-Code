package encoder

import (
	"github.com/rs/zerolog/log"
	"strconv"
	"strings"
)

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
	sValue := strconv.FormatFloat(p.Value, 'f', 2, 64)
	return sNbZeros + ";" + sValue
}

// ToByte returns the representation of the pair
// in byte format, useful for bandwith limited transmissions
func (p *RLEPair) ToByte() []byte {
	bNbZeros := byte(p.NbZeros)
	bValue := byte(p.Value)
	return []byte{bNbZeros, bValue}
}

// RLEPairFromString returns a RLEPair from its representation
// in a string. Useful to get back data from huffman
func RLEPairFromString(data string) *RLEPair {
	args := strings.Split(data, ";")
	nbZeros, errInt := strconv.Atoi(args[0])
	value, errFloat := strconv.ParseFloat(args[1], 64)

	if errInt != nil || errFloat != nil {
		log.Error().Str("data", data).Msg("Cannot parse string to RLEPair")
		return nil
	}

	return &RLEPair{
		NbZeros: nbZeros,
		Value: value,
	}
}

// RLEPairFromByte returns a RLEPair from its binary representation
func RLEPairFromByte(data []byte) *RLEPair {
	return &RLEPair{
		NbZeros: int(data[0]),
		Value: float64(data[1]),
	}
}