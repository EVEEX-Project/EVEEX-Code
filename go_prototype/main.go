package main

import (
	"eveex/pkg/image"
)

func main() {
	// setting up the logger
	closeFile := setupLogger()
	defer closeFile()
	// printing the pretty welcome message
	helloWorld("0.1.0")

	_, _ = image.LoadImageFromFile("assets/discord_logo.png")
}
