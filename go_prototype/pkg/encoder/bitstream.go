package encoder

type Bitstream struct {
	size int
	data []byte
}

func (bs *Bitstream) GetData() []byte {
	return bs.data
}

func NewBitstreamWithSize(size int) *Bitstream {
	return &Bitstream{
		size: size,
		data: make([]byte, size),
	}
}

func NewEmptyBitstream() *Bitstream {
	return &Bitstream{
		size: 0,
		data: make([]byte, 0),
	}
}
