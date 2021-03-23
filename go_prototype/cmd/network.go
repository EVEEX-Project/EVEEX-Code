package cmd

import (
	"eveex/pkg/encoder"
	"eveex/pkg/image"
	"eveex/pkg/network"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
)

var networkDebug bool
var networkListen bool
var networkPort int
var networkHost string

// networkCmd represents the network command
var networkCmd = &cobra.Command{
	Use:   "network",
	Short: "Network utils for client/server",
	Long: `======================== Help: Nework command ========================
Helper command to try and test the client/server
connectivity. Using different flags, one can start
a server on a specific port and connect to another
server.

Example:
  ./eveex network --listen --port 12345 --addr 127.0.0.1
  ./eveex network --port 12345 --addr 127.0.0.1`,
	Run: func(cmd *cobra.Command, args []string) {
		// setting up the logger
		closeFile := setupLogger()
		defer closeFile()
		if networkDebug {
			zerolog.SetGlobalLevel(zerolog.DebugLevel)
		}
		printLogSeparator()

		if networkListen {
			// start a server
			log.Info().Str("addr", networkHost).Int("port", networkPort).Msg("Starting server")

			server := network.NewTCPServer(networkHost, networkPort)
			server.StartServer()
			defer server.CloseServer()

			server.HandleRequests()
		} else {
			// start a client
			log.Info().Str("addr", networkHost).Int("port", networkPort).Msg("Starting client")

			client := network.NewTCPClient(networkHost, networkPort)
			client.Connect()

			img, err := image.LoadImageFromFile("assets/20px.png")
			if err != nil {
				log.Fatal().Str("filename", args[0]).Msgf("Cannot load image : %s\n", err.Error())
			}
			bs := encoder.EncodeImage(img,20, 8)

			// sending encoded data to server
			client.SendBytes(bs.GetHeader())
			// receiving the server's response
			client.GetServerAnswer()

			client.SendBytes(bs.GetDict())
			client.GetServerAnswer()
			client.SendBytes(bs.GetBody())
			client.GetServerAnswer()
			client.SendBytes(bs.GetTail())
			client.GetServerAnswer()
		}
	},
}

func init() {
	rootCmd.AddCommand(networkCmd)

	// Local flags definition
	networkCmd.Flags().BoolVarP(&networkDebug, "debug", "d", false, "Print debugging logs of the network process")
	networkCmd.Flags().StringVarP(&networkHost, "addr", "a", "127.0.0.1", "Address of the server")
	networkCmd.Flags().IntVarP(&networkPort, "port", "p", 12345, "Port of the server")
	networkCmd.Flags().BoolVarP(&networkListen, "listen", "l", false, "Start a server instead of a client")
}
