package encoder

import (
	"bytes"
	"encoding/binary"
	"encoding/gob"
	"github.com/rs/zerolog/log"
)

type Bitstream struct {
	size int
	header []byte
	dictionary []byte
	body []byte
	tail []byte
}

func (bs *Bitstream) GetHeader() []byte {
	return bs.header
}

func (bs *Bitstream) GetBody() []byte {
	return bs.body
}

func (bs *Bitstream) GetDict() []byte {
	return bs.dictionary
}

func (bs *Bitstream) GetTail() []byte {
	return bs.tail
}

func (bs *Bitstream) GetStream() []byte {
	var output []byte
	output = append(output, bs.header...)
	output = append(output, bs.dictionary...)
	output = append(output, bs.body...)
	output = append(output, bs.tail...)

	return output
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

func NewBitstreamFromData(dictionary map[string][]byte, rlePairs [][]*RLEPair, macroblocksize uint16, width uint16, height uint16 ,frameid uint16, dictPacketIndex uint16, bodyPacketIndex uint16) *Bitstream {

	var bFrameID = make([]byte, 2)
	var u16buf = make([]byte, 2)

	// HEADER - 48 bits
	binary.LittleEndian.PutUint16(bFrameID, frameid)
	header := bFrameID[:]
	header = append(header, byte(0)) // 0 = HEADER_MSG

	binary.LittleEndian.PutUint16(u16buf, width)
	header = append(header, u16buf...)

	binary.LittleEndian.PutUint16(u16buf, height)
	header = append(header, u16buf...)

	binary.LittleEndian.PutUint16(u16buf, macroblocksize)
	header = append(header, u16buf...)

	// DICT - 50 + dictionary size
	dicti := bFrameID[:]
	header = append(header, byte(1)) // 1 = DICTI_MSG

	binary.LittleEndian.PutUint16(u16buf, dictPacketIndex)
	dicti = append(dicti, u16buf...)

	// getting dict bytes
	var buf bytes.Buffer
	enc := gob.NewEncoder(&buf)
	err := enc.Encode(dictionary)
	if err != nil { log.Error().Msg("Failed to encode dictionary") }

	binary.LittleEndian.PutUint16(u16buf, uint16(len(buf.Bytes())))
	dicti = append(dicti, u16buf...)
	dicti = append(dicti, buf.Bytes()...)

	//BODY - head = 68 + 1st macroblock data
	var body []byte

	// each macrobloc - 68 bits + macroblock data
	for macroblocIdx := 0; macroblocIdx < len(rlePairs); macroblocIdx++ {
		body = append(body, bFrameID...)
		body = append(body, byte(2)) // 2 = BODY_MSG

		binary.LittleEndian.PutUint16(u16buf, uint16(macroblocIdx))
		body = append(body, u16buf...)

		binary.LittleEndian.PutUint16(u16buf, bodyPacketIndex)
		body = append(body, u16buf...)

		binary.LittleEndian.PutUint16(u16buf, uint16(len(rlePairs[macroblocIdx])))
		body = append(body, u16buf...)

		var bData []byte
		for _, pair := range rlePairs[macroblocIdx] {
			bData = append(bData, pair.ToByte()...)
		}
		body = append(body, bData...)
	}

	// TAIL -
	tail := bFrameID[:]
	tail = append(tail, byte(3)) // 3 = END_MSG

	return &Bitstream {
		size: len(body) + len(header) + len(tail) + len(dicti),
		header: header,
		dictionary: dicti,
		body:   body,
		tail: 	tail,
	}
}