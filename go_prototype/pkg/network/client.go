package network

import (
	"bufio"
	"github.com/rs/zerolog/log"
	"net"
	"os"
	"strconv"
	"time"
)

type TCPClient struct {
	address string
	port int
	conn net.Conn
}

func NewTCPClient(address string, port int) *TCPClient{
	return &TCPClient{address: address, port: port}
}

func (c *TCPClient) Connect() {
	var err error
	c.conn, err = net.Dial("tcp", c.getDest())
	if err != nil {
		log.Error().Err(err).Msg("Error while connecting to client")
		os.Exit(1)
	}
}

func (c *TCPClient) SendString(data string) {
	log.Debug().Str("data", data).Msg("Sending string to server")
	_ = c.conn.SetWriteDeadline(time.Now().Add(1 * time.Second))
	_, err := c.conn.Write([]byte(data))
	if err != nil { log.Error().Err(err).Msg("Error while printing to stream") }
}

func (c *TCPClient) SendBytes(data []byte) {
	log.Debug().Int("data_length", len(data)).Msg("Sending string to server")
	_ = c.conn.SetWriteDeadline(time.Now().Add(1 * time.Second))
	_, err := c.conn.Write(data)
	if err != nil { log.Error().Err(err).Msg("Error while printing to stream") }
}

func (c *TCPClient) GetServerAnswer() {
	scanner := bufio.NewScanner(c.conn)
	for {
		ok := scanner.Scan()
		text := scanner.Text()

		if !ok {
			log.Warn().Msg("Connexion closed with server.")
			break
		}

		log.Info().Msgf("Received from server: %s", text)
	}
}

func (c *TCPClient) getDest() string {
	return c.address + ":" + strconv.Itoa(c.port)
}