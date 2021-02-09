package main

import (
	"eveex/pkg/encoder"
	"eveex/pkg/huffman"
	"eveex/pkg/image"
	"fmt"
)

func main() {
	// setting up the logger
	closeFile := setupLogger()
	defer closeFile()
	// printing the pretty welcome message
	helloWorld("0.1.0")

	img, _ := image.LoadImageFromFile("assets/image_res.png")
	macroblocs := encoder.SplitInMacroblocs(*img, 10)

	// taking the first one for tests
	mb 				:= macroblocs[0]
	dctMbR, _, _ 	:= encoder.DCT(mb)
	zzVals 			:= encoder.ZigzagLinearisation(dctMbR)
	quantVals 		:= encoder.Quantization(zzVals, 0.25)
	rlePairs 		:= encoder.RunLevel(quantVals)
	nodeList		:= huffman.RLEPairsToNodes(rlePairs)

	fmt.Printf("%v\n", nodeList)
}
