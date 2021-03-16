package decoder

import (
	"bytes"
	"encoding/binary"
	"encoding/gob"
	"eveex/pkg/encoder"
	"github.com/rs/zerolog/log"
)

type Bitstream struct {
	FrameID uint16
	Width 	uint16
	Height 	uint16
	MacroBlockSize uint16
	RlePairs [][]*encoder.RLEPair
	Symbols map[string][]byte

	Complete bool
}

func (bs *Bitstream) DecodePacket(stream []byte) {
	// getting the type of data
	var packetType = int(stream[2])

	switch (packetType) {
	case 0: // header
		bs.DecodeHeader(stream)
		break
	case 1: // dictionary
		bs.DecodeDictionary(stream)
		break
	case 2: // body
		bs.DecodeBody(stream)
		break
	case 3: // tail
		// received end of frame
		bs.Complete = true
		break
	default:
		log.Error().Int("packetTypeNb", packetType).Msg("Wrong packet Type")
		break
	}
}

func (bs *Bitstream) DecodeHeader(header []byte) {
	bs.FrameID = binary.LittleEndian.Uint16(header[:2])
	bs.Width = binary.LittleEndian.Uint16(header[3:5])
	bs.Height = binary.LittleEndian.Uint16(header[5:7])
	bs.MacroBlockSize = binary.LittleEndian.Uint16(header[7:9])

	// setup the other vars
	bs.RlePairs = make([][]*encoder.RLEPair, (bs.Width / bs.MacroBlockSize) * (bs.Height / bs.MacroBlockSize))
}

func (bs *Bitstream) DecodeDictionary(dicti []byte) {
	//var dictPktIdx = binary.LittleEndian.Uint16(dicti[3:5])
	var dataSize = binary.LittleEndian.Uint16(dicti[5:7])
	var dictData = dicti[7:7+dataSize]

	var dict map[string][]byte
	dec := gob.NewDecoder(bytes.NewBuffer(dictData))
	err := dec.Decode(&dict)
	if err != nil { log.Error().Msg("Failed to decode dictionary") }
	bs.Symbols = dict
}

func (bs *Bitstream) DecodeBody(body []byte) {
	var macroblockIdx = binary.LittleEndian.Uint16(body[3:5])
	// var bodyPktIdx = binary.LittleEndian.Uint16(body[5:7])
	var dataSize = binary.LittleEndian.Uint16(body[7:9])
	var data = body[9:9+dataSize]

	var pairs []*encoder.RLEPair
	for k := 0; k < int(dataSize); k += 12 {
		pairs = append(pairs, encoder.RLEPairFromByte(data[k:k+12]))
	}
	bs.RlePairs[macroblockIdx] = pairs
}