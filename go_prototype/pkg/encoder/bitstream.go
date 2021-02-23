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
	return NewBitstreamWithSize(0)
}


func dec2bin(dec int, size int) []byte {
	dec64 := int64(dec)
	bin := strconv.FormatInt(dec64, 2)
	bin2 := fmt.Sprintf("%0*v", size, bin) // choisi la taille du binaire : '101010' devient '0000000000101010' pour du 16bits
	binByte := []byte{0}
	if bin2[0] == '1'{
		binByte = []byte{1}
	}
	for i := 1; i < len(bin2); i++{
		if bin2[i] == '1'{
			binByte = append(binByte,[]byte{1}...)
		} else {
			binByte = append(binByte,[]byte{0}...)
		}
	}
	return binByte
}

func CreateBitstream(dict []byte, macroblocks []string, macroblocksize int, width int, height int ,frameid int) []byte {


	// HEADER
	header := dec2bin(frameid, 16 )
	header = append(header, dec2bin(0,2)...) // 0 = HEADER_MSG
	header = append(header, dec2bin(width,12)...)
	header = append(header, dec2bin(height,12)...)
	header = append(header, dec2bin(macroblocksize,6)...)

	// DICT



	return header // juste pour éviter que le complilateur râle (en sortie il veut un objet de type []byte)
}
