package encoder

import (
	"eveex/pkg/huffman"
	"eveex/pkg/image"
	"eveex/pkg/types"
	"github.com/rs/zerolog/log"
)

type JobResult struct {
	rlePairs []*types.RLEPair
	index int
}

type JobRequest struct {
	img *image.Image
	index int
}

func EncodeImage(img *image.Image, mbSize int, nbWorkers int) *Bitstream {
	macroblocs := SplitInMacroblocs(*img, mbSize)

	// final array
	var rlePairs [][]*types.RLEPair
	for r := 0; r < len(macroblocs); r++ {
		rlePairs = append(rlePairs, []*types.RLEPair{})
	}

	// setting up jobs and their result

	var jobs = make(chan JobRequest, len(macroblocs))
	var results = make(chan JobResult, img.GetHeight()/len(macroblocs))

	// creating workers
	for w := 0; w < nbWorkers; w++ {
		go encodeWorker(jobs, results)
	}
	// sending jobs
	for k, mb := range macroblocs {
		jobs <- JobRequest{
			img:   &mb,
			index: k,
		}
	}
	close(jobs)

	// getting back the results
	for r := 0; r < len(macroblocs); r++ {
		var res = <- results
		rlePairs[res.index] = res.rlePairs
	}
	close(results)

	// huffman
	var pairList []*types.RLEPair
	for k := 0; k < len(rlePairs); k++ {
		pairList = append(pairList, rlePairs[k]...)
	}
	nodeList		:= huffman.RLEPairsToNodes(pairList)
	root 			:= huffman.GenerateTreeFromList(nodeList)

	encodingDict := make(map[string][]byte)
	huffman.GenerateEncodingDict(&encodingDict, root, []byte{})

	bs := NewBitstreamFromData(encodingDict, rlePairs, uint16(mbSize), uint16(img.GetWidth()), uint16(img.GetHeight()), 0, 0, 0)
	//log.Info().Bytes("header", bs.GetHeader()).Bytes("body", bs.GetBody()).Msg("Bitstream")
	log.Info().
		Int("header_length", len(bs.GetHeader())).
		Int("body_length", len(bs.GetBody())).
		Int("dict_length", len(bs.GetDict())).
		Int("stream_length", len(bs.GetStream())).Msg("Getting bitstream")

	return bs
}

func encodeWorker(jobs <-chan JobRequest, results chan <- JobResult) {
	for mb := range jobs {
		threshold := 5.0
		dctMbR, dctMbG, dctMbB := DCT(*mb.img)
		zzValsR, zzValsG, zzValsB := ZigzagLinearisation(dctMbR), ZigzagLinearisation(dctMbG), ZigzagLinearisation(dctMbB)

		zzVals := make([]float64, 3 * len(zzValsR))
		zzVals = append(zzVals, zzValsR...)
		zzVals = append(zzVals, zzValsG...)
		zzVals = append(zzVals, zzValsB...)
		quantVals := Quantization(zzVals, threshold)

		results <- JobResult{RunLevel(quantVals), mb.index}
	}
}
