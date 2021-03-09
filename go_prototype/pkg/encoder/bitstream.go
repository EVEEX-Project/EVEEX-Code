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
			binByte = append(binByte,[]byte{1}...)
		} else {
			binByte = append(binByte,[]byte{0}...)
		}
	}
	return binByte
}

func CreateBitstream(dict []byte, macroblocks [][]byte, macroblocksize int, width int, height int ,frameid int, index_paquet_dict int, index_paquet_body int) *Bitstream {


	// HEADER
	header := dec2bin(frameid, 16 )
	header = append(header, dec2bin(0,2)...) // 0 = HEADER_MSG
	header = append(header, dec2bin(width,12)...)
	header = append(header, dec2bin(height,12)...)
	header = append(header, dec2bin(macroblocksize,6)...)

	// DICT
	dicti := dec2bin(frameid, 16)
	dicti = append(dicti, dec2bin(1, 2)...) // 1 = DICTI_MSG
	dicti = append(dicti, dec2bin(index_paquet_dict, 16)...)
	dicti = append(dicti, dec2bin(len(dict),16)...)
	dicti = append(dicti, dict...)

	//BODY
	body := dec2bin(frameid, 16)
	body = append(body, dec2bin(2, 2)...) // 2 = BODY_MSG
	body = append(body, dec2bin(0, 16)...)
	body = append(body, dec2bin(index_paquet_body,16)...)//index_paquet
	body = append(body, dec2bin(len(macroblocks[0]),16)...)
	body = append(body, macroblocks[0]...)

	for num_macroblock := 1; num_macroblock < len(macroblocks); num_macroblock++ {
		body = append(body, dec2bin(frameid,16)...)
		body = append(body, dec2bin(2, 2)...) // 2 = BODY_MSG
		body = append(body, dec2bin(num_macroblock, 16)...)
		body = append(body, dec2bin(index_paquet_body,16)...) //index_paquet
		body = append(body, dec2bin(len(macroblocks[num_macroblock]),16)...)
		body = append(body, macroblocks[num_macroblock]...)
	}

	tail := dec2bin(frameid, 16)
	tail = append(tail,dec2bin(3,2)...) // 3 = END_MSG


	sortie := append(dicti,body...)
	sortie = append(sortie,tail...)

	return &Bitstream {
		size: len(sortie)+len(header),
		header: header,
		body: sortie,
	} // juste pour éviter que le complilateur râle (en sortie il veut un objet de type []byte)
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