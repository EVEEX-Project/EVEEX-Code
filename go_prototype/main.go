package main

import (
	"bufio"
	"eveex/pkg/image"
	"fmt"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"io"
	"os"
)

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
	fmt.Printf("─────────────────────\033[1;37m LOGS \033[0m────────────────────────\n")
}

func testLogs() {
	log.Trace().Msg("Trace msg")
	log.Debug().Msg("Debug msg")
	log.Info().Msg("Info msg")
	log.Warn().Msg("Warn msg")
	log.Error().Msg("Error msg")
}

func main() {
	// create a temp file
	logFile, err := os.Create("logs.log")
	if err != nil {
		// Can we log an error before we have our logger? :)
		log.Error().Err(err).Msg("there was an error creating a temporary file four our log")
	}
	fileWriter := bufio.NewWriter(logFile)
	defer func() {
		fileWriter.Flush()
		logFile.Close()
	}()

	// logger config
	var writers []io.Writer
	writers = append(writers, zerolog.ConsoleWriter{Out: os.Stderr})
	writers = append(writers, fileWriter)
	log.Logger = zerolog.New(io.MultiWriter(writers...)).With().Timestamp().Logger()

	zerolog.TimeFieldFormat = zerolog.TimeFormatUnix

	helloWorld("0.1.0")
	img, _ := image.LoadImageFromFile("assets/discord_logo.png")

	w, h := img.GetSize()
	log.Info().Msgf("Loaded an Image of size : %dpx x %dpx with %d channels", w, h, img.GetChannels())

	testLogs()
}
