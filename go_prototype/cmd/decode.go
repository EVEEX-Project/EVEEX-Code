package cmd

import (
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
	"os"
	"runtime/pprof"
)

var decodeOutputPath string
var decodeDebug bool
var decodeMacroblocSize int
var startDecodeCPUProfiling bool

// encodeCmd represents the encode command
var decodeCmd = &cobra.Command{
	Use:   "decode <path to file>",
	Args: cobra.ExactArgs(1),
	Short: "Decode an image or a video file",
	Long: `======================== Help: Decode command =======================
Using the EVEEX decoding algorithm, decodes a bitstream
into an image or video file. Using the '-o' flag,
on can output the content to a specific file. The default
output is the standard output (console). Using the '-d' 
flag one can print the debug messages.

Example:
  ./eveex decode assets/20px.dat
  ./eveex decode --debug assets/20px.dat
  ./eveex decode --output=res.png assets/20px.dat`,
	Run: func(cmd *cobra.Command, args []string) {
		// starting pprof
		if startDecodeCPUProfiling {
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
		if decodeDebug {
			zerolog.SetGlobalLevel(zerolog.DebugLevel)
		}
		printLogSeparator()


	},
}

func init() {
	rootCmd.AddCommand(decodeCmd)

	// Local flags definition
	decodeCmd.Flags().StringVarP(&encodeOutputPath, "output", "o", "", "Exports the image data to a file")
	decodeCmd.Flags().BoolVarP(&encodeDebug, "debug", "d", false, "Print debugging logs of the decoding process")
	decodeCmd.Flags().IntVarP(&encodeMacroblocSize, "mbsize", "m", 20, "Change the size of the macrobloc")
	decodeCmd.Flags().BoolVarP(&startDecodeCPUProfiling, "cpuprofile", "p", false, "Start the profiling of EVEEX decoder")
}
