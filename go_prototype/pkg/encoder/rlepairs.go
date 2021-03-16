package encoder

import (
	"github.com/rs/zerolog/log"
	"math"
	"strconv"
	"strings"
	"encoding/binary"
)

// RLEPair contains the data associated
// to a RLE pair
type RLEPair struct {
	NbZeros uint32
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
	bNbZeros := make([]byte, 4)
	binary.LittleEndian.PutUint32(bNbZeros, p.NbZeros)
	bValue := make([]byte, 8)
	binary.LittleEndian.PutUint64(bValue, math.Float64bits(p.Value))
	return append(bNbZeros, bValue...)
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
		NbZeros: uint32(nbZeros),
		Value: value,
	}
}

// RLEPairFromByte returns a RLEPair from its binary representation
func RLEPairFromByte(data []byte) *RLEPair {
	bNbZeros := data[:4]
	bValue := data[4:]

	nbZeros := binary.LittleEndian.Uint32(bNbZeros)
	value := math.Float64frombits(binary.LittleEndian.Uint64(bValue))
	return &RLEPair{
		NbZeros: nbZeros,
		Value: value,
	}
}