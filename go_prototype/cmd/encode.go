package cmd

import (
	"eveex/pkg/encoder"
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

		// encoding
		encoder.EncodeImage(img, encodeMacroblocSize, 8)
	},
}

func init() {
	rootCmd.AddCommand(encodeCmd)

	// Local flags definition
	encodeCmd.Flags().StringVarP(&encodeOutputPath, "output", "o", "", "Exports the bitstream to a file")
	encodeCmd.Flags().BoolVarP(&encodeDebug, "debug", "d", false, "Print debugging logs of the encoding process")
	encodeCmd.Flags().IntVarP(&encodeMacroblocSize, "mbsize", "m", 20, "Change the size of the macrobloc")
	encodeCmd.Flags().BoolVarP(&startEncodeCPUProfiling, "cpuprofile", "p", false, "Start the profiling of EVEEX encoder")
}
