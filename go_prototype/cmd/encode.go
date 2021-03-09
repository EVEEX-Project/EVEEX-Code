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
		var rlePairs []encoder.RLEPair

		// setting up jobs and their result
		var jobs = make(chan *image.Image, len(macroblocs))
		var results = make(chan []encoder.RLEPair, len(macroblocs))

		// creating workers
		for w := 0; w < 8; w++ {
			go encodeWorker(jobs, results)
		}
		// sending jobs
		for _, mb := range macroblocs {
			jobs <- &mb
		}
		close(jobs)

		// getting back the results
		for r := 0; r < len(macroblocs); r++ {
			var res = <- results
			rlePairs = append(rlePairs, res...)
		}
		close(results)

		// huffman
		nodeList		:= huffman.RLEPairsToNodes(rlePairs)
		root 			:= huffman.GenerateTreeFromList(nodeList)

		encodingDict := make(map[string]string)
		huffman.GenerateEncodingDict(&encodingDict, root, "")

		/*huffman.PrintTree(root)

		for key, val := range encodingDict {
			log.Info().Msgf("%s --> %s", key, val)
		}

		bs := encoder.EncodePairs(rlePairs, encodingDict)
		log.Info().Msgf("Bistream: %s", bs.GetData())*/
	},
}

func encodeWorker(jobs <-chan *image.Image, results chan <- []encoder.RLEPair) {
	for mb := range jobs {
		threshold := 5.0
		dctMbR, dctMbG, dctMbB := encoder.DCT(*mb)
		zzValsR, zzValsG, zzValsB := encoder.ZigzagLinearisation(dctMbR), encoder.ZigzagLinearisation(dctMbG), encoder.ZigzagLinearisation(dctMbB)

		zzVals := make([]float64, 3 * len(zzValsR))
		zzVals = append(zzVals, zzValsR...)
		zzVals = append(zzVals, zzValsG...)
		zzVals = append(zzVals, zzValsB...)
		quantVals := encoder.Quantization(zzVals, threshold)

		results <- encoder.RunLevel(quantVals)
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
