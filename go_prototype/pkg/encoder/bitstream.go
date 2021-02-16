package encoder

import (
	"fmt"
	"strconv"
)

type Bitstream struct {
	size int
	data []byte
}

func (bs *Bitstream) GetData() []byte {
	return bs.data
}

func NewBitstreamWithSize(size int) *Bitstream {
	return &Bitstream{
		size: size,
		data: make([]byte, size),
	}
}

func NewEmptyBitstream() *Bitstream {
	return &Bitstream{
		size: 0,
		data: make([]byte, 0),
	}
}

func dec2bin(dec int, size int) string {
	dec64 := int64(dec)
	bin := strconv.FormatInt(dec64, 2)
	bin2 := fmt.Sprintf("%0*v", size, bin) // choisi la taille du binaire : '101010' devient '0000000000101010' pour du 16bits

	return bin2
}
