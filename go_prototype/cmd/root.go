package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"os"
)

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "eveex",
	Short: "ENSTA B. Video Encoder EXperimental",
	Long: `An open-source video encoder made to work
primarely on embedded devices such as a Raspberry Pi.
This encoder is heavily inspired by the MJPEG format
while using an open-source implementation`,
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() {
	helloWorld("0.2.5")
}