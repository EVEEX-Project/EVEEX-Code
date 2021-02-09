package cmd

import (
	"eveex/pkg/encoder"
	"eveex/pkg/huffman"
	"eveex/pkg/image"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
)

var encodeOutputPath string
var encodeDebug bool
var encodeMacroblocSize int

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
		// setting up the logger
		closeFile := setupLogger()
		defer closeFile()
		if encodeDebug {
			zerolog.SetGlobalLevel(zerolog.DebugLevel)
		}
		printLogSeparator()

		img, _ := image.LoadImageFromFile(args[0])
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
	},
}

func init() {
	rootCmd.AddCommand(encodeCmd)

	// Local flags definition
	encodeCmd.Flags().StringVarP(&encodeOutputPath, "output", "o", "", "Exports the bitstream to a file")
	encodeCmd.Flags().BoolVarP(&encodeDebug, "debug", "d", false, "Print debugging logs of the encoding process")
	encodeCmd.Flags().IntVarP(&encodeMacroblocSize, "mbsize", "m", 20, "Change the size of the macrobloc")
}
