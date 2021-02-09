package main

import (
	"eveex/pkg/encoder"
	"eveex/pkg/huffman"
	"eveex/pkg/image"
	"github.com/rs/zerolog/log"
)

func main() {
	// setting up the logger
	closeFile := setupLogger()
	defer closeFile()
	// printing the pretty welcome message
	helloWorld("0.1.0")

	img, _ := image.LoadImageFromFile("assets/20px.png")
	macroblocs := encoder.SplitInMacroblocs(*img, 20)

	// taking the first one for tests
	mb 				:= macroblocs[0]
	dctMbR, _, _ 	:= encoder.DCT(mb)
	zzVals 			:= encoder.ZigzagLinearisation(dctMbR)
	quantVals 		:= encoder.Quantization(zzVals, 5)
	rlePairs 		:= encoder.RunLevel(quantVals)

	// huffman
	nodeList		:= huffman.RLEPairsToNodes(rlePairs)
	root := huffman.GenerateTreeFromList(nodeList)

	encodingDict := make(map[string]string)
	huffman.GenerateEncodingDict(&encodingDict, root, "")

	huffman.PrintTree(root)

	for key, val := range encodingDict {
		log.Info().Msgf("%s --> %s", key, val)
	}
}
