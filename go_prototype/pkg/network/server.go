package network

import (
	"bufio"
	"github.com/rs/zerolog/log"
	"net"
	"strconv"
)

type TCPServer struct {
	address string
	port int
	listener net.Listener
}

func NewTCPServer(address string, port int) *TCPServer{
	return &TCPServer{address: address, port: port}
}

func (s *TCPServer) StartServer() {
	var err error
	s.listener, err = net.Listen("tcp", s.getSrc())
	if err != nil { log.Error().Err(err) }
	log.Info().Msgf("Listening on %s", s.getSrc())
}

func (s *TCPServer) HandleRequests() {
	for {
		conn, err := s.listener.Accept()
		if err != nil { log.Error().Err(err) }

		s.requestHandler(conn)
	}
}

func (s *TCPServer) requestHandler(conn net.Conn) {
	log.Info().Str("addr", conn.RemoteAddr().String()).Msg("Client connected")
	scanner := bufio.NewScanner(conn)

	for {
		ok := scanner.Scan()

		if !ok {
			log.Warn().Msg("Connexion closed with client")
			break
		}

		text := scanner.Text()
		log.Info().Msgf("Got from client: %s", text)

		// sending back the data
		conn.Write([]byte(text + "\n"))
	}
}

func (s *TCPServer) CloseServer() {
	log.Info().Msg("Closing the server")
	err := s.listener.Close()
	if err != nil { log.Error().Err(err) }
}

func (s *TCPServer) getSrc() string {
	return s.address + ":" + strconv.Itoa(s.port)
}