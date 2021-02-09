package cmd

import (
	"bufio"
	"eveex/pkg/encoder"
	"eveex/pkg/huffman"
	"eveex/pkg/image"
	"fmt"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"io"
	"os"
)

// helloWorld prints a pretty welcome message
// in the console
func helloWorld(version string) {
	fmt.Printf("\033[1;35m            _______    _______________  __\n")
	fmt.Printf("           / ____/ |  / / ____/ ____/ |/ /\n")
	fmt.Printf("          / __/  | | / / __/ / __/  |   /\n")
	fmt.Printf("         / /___  | |/ / /___/ /___ /   |\n")
	fmt.Printf("        /_____/  |___/_____/_____//_/|_|\n")
	fmt.Printf("          ___  ___  / __/ _ \\/ ___/ _ |\n")
	fmt.Printf("         / _ \\/ _ \\/ _// ___/ (_ / __ |\n")
	fmt.Printf("         \\___/_//_/_/ /_/   \\___/_/ |_|\n\n")
	fmt.Printf("\033[0;36m32-bit RISC-V Open Source video compression program\n")
	fmt.Printf("                version \033[0;31m%s\033[0m\n\n", version)
}

func printLogSeparator() {
	fmt.Printf("─────────────────────\033[1;37m LOGS \033[0m────────────────────────\n")
}

// setupLogger setups the configuration of the logger
// including the logging level and the logging file
func setupLogger() func() {
	zerolog.SetGlobalLevel(zerolog.InfoLevel)

	// create a logging file
	logFile, err := os.Create("logs.log")
	if err != nil {
		// Can we log an error before we have our logger? :)
		log.Error().Err(err).Msg("there was an error creating the log file")
	}
	fileWriter := bufio.NewWriter(logFile)
	defer func() {

	}()

	// logger writers
	var writers []io.Writer
	// console logger
	writers = append(writers, zerolog.ConsoleWriter{Out: os.Stderr})
	// file logger
	writers = append(writers, fileWriter)
	log.Logger = zerolog.New(io.MultiWriter(writers...)).With().Timestamp().Logger()

	// unix time format is often the fastest one
	zerolog.TimeFieldFormat = zerolog.TimeFormatUnix

	// return the function to close the file
	return func () {
		errFlush := fileWriter.Flush()
		errClose := logFile.Close()
		if errFlush != nil || errClose != nil {
			log.Error().Msg("cannot properly save/close the logging file")
		}
	}
}

// testLogs prints defaults messages for
// each logging level (except fatal)
func testLogs() {
	log.Trace().Msg("Trace msg")
	log.Debug().Msg("Debug msg")
	log.Info().Msg("Info msg")
	log.Warn().Msg("Warn msg")
	log.Error().Msg("Error msg")
}

func defau() {
	// setting up the logger
	closeFile := setupLogger()
	defer closeFile()
	// printing the pretty welcome message
	helloWorld("0.1.2")

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