package encoder

import (
	"fmt"
	"strconv"
)

type Bitstream struct {
	size int
	header []byte
	body []byte
}

func (bs *Bitstream) GetHeader() []byte {
	return bs.header
}

func (bs *Bitstream) GetBody() []byte {
	return bs.body
}

func NewBitstreamWithSize(size int) *Bitstream {
	return &Bitstream{
		size: size,
		header: make([]byte, 100),
		body: make([]byte, size),
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
			binByte = append(binByte, byte(1))
		} else {
			binByte = append(binByte, byte(0))
		}
	}
	return binByte
}

func NewBitstreamFromData(dictionary []byte, macroblocks [][]byte, macroblocksize int, width int, height int ,frameid int, dictPacketIndex int, bodyPacketIndex int) *Bitstream {

	// HEADER - 48 bits
	header := dec2bin(frameid, 16 )
	header = append(header, dec2bin(0,2)...) // 0 = HEADER_MSG
	header = append(header, dec2bin(width,12)...)
	header = append(header, dec2bin(height,12)...)
	header = append(header, dec2bin(macroblocksize,6)...)

	// DICT - 50 + dictionary size
	dicti := dec2bin(frameid, 16)
	dicti = append(dicti, dec2bin(1, 2)...) // 1 = DICTI_MSG
	dicti = append(dicti, dec2bin(dictPacketIndex, 16)...)
	dicti = append(dicti, dec2bin(len(dictionary),16)...)
	dicti = append(dicti, dictionary...)

	//BODY - head = 68 + 1st macroblock data
	var body []byte

	// each macrobloc - 68 bits + macroblock data
	for macroblocIdx := 0; macroblocIdx < len(macroblocks); macroblocIdx++ {
		body = append(body, dec2bin(frameid,16)...)
		body = append(body, dec2bin(2, 2)...) // 2 = BODY_MSG
		body = append(body, dec2bin(macroblocIdx, 16)...)
		body = append(body, dec2bin(bodyPacketIndex,16)...) //index_paquet
		body = append(body, dec2bin(len(macroblocks[macroblocIdx]),16)...)
		body = append(body, macroblocks[macroblocIdx]...)
	}

	// TAIL -
	tail := dec2bin(frameid, 16)
	tail = append(tail, dec2bin(3,2)...) // 3 = END_MSG

	// TOTAL
	output := append(dicti, body...)
	output = append(output, tail...)

	return &Bitstream {
		size:   len(output)+len(header),
		header: header,
		body:   output,
	}
}

// Decode will return the frameid, the dictionary, the macroblocs size, the width
// and height of the image
func (bs *Bitstream) Decode() (int, []byte, string, int, int, int) {
	var frameID int
	var dict []byte
	var data string
	var macroblocSize int
	var height int
	var width int

	return frameID, dict, data, macroblocSize, height, width
}