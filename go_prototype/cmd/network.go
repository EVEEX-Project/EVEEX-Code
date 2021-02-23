package cmd

import (
	"bytes"
	"eveex/pkg/huffman"
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

			/*
			// example of RLE pairs
			var rlePairs []encoder.RLEPair
			pair1 := encoder.RLEPair{NbZeros: 5, Value: 7}
			pair2 := encoder.RLEPair{NbZeros: 15, Value: 2}
			rlePairs = append(rlePairs, pair1, pair2)

			// generating the encoding dictionary
			nodeList := huffman.RLEPairsToNodes(rlePairs)
			root := huffman.GenerateTreeFromList(nodeList)
			encodingDict := make(map[string]string)
			huffman.GenerateEncodingDict(&encodingDict, root, "")
			nbKeys := len(encodingDict)
			log.Debug().Int("Number of keys", nbKeys).Msg("The encoding dictionary was successfully generated")

			// encoding the RLE pairs
			encodedRlePairs := encoder.EncodePairs(rlePairs, encodingDict)
			encodedData := string(encodedRlePairs.GetData())
			log.Debug().Str("Encoded data", encodedData).Msg("The RLE pairs were successfully encoded.")

			client.SendString(encodedData)
			client.GetServerAnswer()
			*/

			sentence := "ensta bretagne ftw"

			// generating the encoding dictionary for the given sentence
			nodes := huffman.SplitPhraseInNodes(sentence)
			tree := huffman.GenerateTreeFromList(nodes)
			var encodingDict = map[string]string{}
			huffman.GenerateEncodingDict(&encodingDict, tree, "")
			nbKeys := len(encodingDict)
			log.Debug().Int("Number of keys in dict", nbKeys).Msg("The encoding dictionary was successfully generated")

			// encoding sentence
			var encodedSentence bytes.Buffer
			encodedSentence.WriteString("")
			for i := 0; i < len(sentence); i++ {
				currentLetter := string(sentence[i])
				encodedLetter := encodingDict[currentLetter]
				encodedSentence.WriteString(encodedLetter) // concatenation
			}
			encodedSentence.WriteString("\n")
			log.Debug().Msgf("The sentence was successfully encoded. Encoded data : %s", encodedSentence.String())

			// sending encoded data to server
			client.SendString(encodedSentence.String())

			// receiving the server's response
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
