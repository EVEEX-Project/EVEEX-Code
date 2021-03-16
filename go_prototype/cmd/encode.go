package cmd

import (
	"eveex/pkg/encoder"
	"eveex/pkg/huffman"
	"eveex/pkg/image"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
	"os"
	"runtime/pprof"
)

var encodeOutputPath string
var encodeDebug bool
var encodeMacroblocSize int
var startEncodeCPUProfiling bool

type JobResult struct {
	rlePairs []*encoder.RLEPair
	index int
}

type JobRequest struct {
	img *image.Image
	index int
}

// encodeCmd represents the encode command
var encodeCmd = &cobra.Command{
	Use:   "encode <path to file>",
	Args: cobra.ExactArgs(1),
	Short: "Encode an image or a video file",
	Long: `======================== Help: Encode command )=======================
Using the EVEEX encoding algorithm, encodes an image
or a video file in a bitstream. Using the '-o' flag,
on can output the content to a specific file. The default
output is the standard output (console). Using the '-d' 
flag one can print the debug messages.

Example:
  ./eveex encode assets/20px.png
  ./eveex encode --debug assets/20px.png
  ./eveex encode --output=out.dat assets/20px.png`,
	Run: func(cmd *cobra.Command, args []string) {
		// starting pprof
		if startEncodeCPUProfiling {
			f, err := os.Create("cpuprofile.prof")
			if err != nil {
				log.Fatal().Msg(err.Error())
			}
			_ = pprof.StartCPUProfile(f)
			defer pprof.StopCPUProfile()
		}

		// setting up the logger
		closeFile := setupLogger()
		defer closeFile()
		if encodeDebug {
			zerolog.SetGlobalLevel(zerolog.DebugLevel)
		}
		printLogSeparator()

		img, err := image.LoadImageFromFile(args[0])
		if err != nil {
			log.Fatal().Str("filename", args[0]).Msgf("Cannot load image : %s\n", err.Error())
		}
		macroblocs := encoder.SplitInMacroblocs(*img, encodeMacroblocSize)

		// final array
		var rlePairs [][]*encoder.RLEPair
		for r := 0; r < len(macroblocs); r++ {
			rlePairs = append(rlePairs, []*encoder.RLEPair{})
		}

		// setting up jobs and their result

		var jobs = make(chan JobRequest, len(macroblocs))
		var results = make(chan JobResult, img.GetHeight()/len(macroblocs))

		// creating workers
		for w := 0; w < 8; w++ {
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
		var pairList []*encoder.RLEPair
		for k := 0; k < len(rlePairs); k++ {
			pairList = append(pairList, rlePairs[k]...)
		}
		nodeList		:= huffman.RLEPairsToNodes(pairList)
		root 			:= huffman.GenerateTreeFromList(nodeList)

		encodingDict := make(map[string][]byte)
		huffman.GenerateEncodingDict(&encodingDict, root, []byte{})

		bs := encoder.NewBitstreamFromData(encodingDict, rlePairs, uint16(encodeMacroblocSize), uint16(img.GetWidth()), uint16(img.GetHeight()), 0, 0, 0)
		//log.Info().Bytes("header", bs.GetHeader()).Bytes("body", bs.GetBody()).Msg("Bitstream")
		log.Info().
			Int("header_length", len(bs.GetHeader())).
			Int("body_length", len(bs.GetBody())).
			Int("dict_length", len(bs.GetDict())).
			Int("stream_length", len(bs.GetStream())).Msg("Getting bitstream")
		/*huffman.PrintTree(root)

		for key, val := range encodingDict {
			log.Info().Msgf("%s --> %s", key, val)
		}

		bs := encoder.EncodePairs(rlePairs, encodingDict)
		log.Info().Msgf("Bistream: %s", bs.GetData())*/
	},
}

func encodeWorker(jobs <-chan JobRequest, results chan <- JobResult) {
	for mb := range jobs {
		threshold := 5.0
		dctMbR, dctMbG, dctMbB := encoder.DCT(*mb.img)
		zzValsR, zzValsG, zzValsB := encoder.ZigzagLinearisation(dctMbR), encoder.ZigzagLinearisation(dctMbG), encoder.ZigzagLinearisation(dctMbB)

		zzVals := make([]float64, 3 * len(zzValsR))
		zzVals = append(zzVals, zzValsR...)
		zzVals = append(zzVals, zzValsG...)
		zzVals = append(zzVals, zzValsB...)
		quantVals := encoder.Quantization(zzVals, threshold)

		results <- JobResult{encoder.RunLevel(quantVals), mb.index}
	}
}

func init() {
	rootCmd.AddCommand(encodeCmd)

	// Local flags definition
	encodeCmd.Flags().StringVarP(&encodeOutputPath, "output", "o", "", "Exports the bitstream to a file")
	encodeCmd.Flags().BoolVarP(&encodeDebug, "debug", "d", false, "Print debugging logs of the encoding process")
	encodeCmd.Flags().IntVarP(&encodeMacroblocSize, "mbsize", "m", 20, "Change the size of the macrobloc")
	encodeCmd.Flags().BoolVarP(&startEncodeCPUProfiling, "cpuprofile", "p", false, "Start the profiling of EVEEX encoder")
}
