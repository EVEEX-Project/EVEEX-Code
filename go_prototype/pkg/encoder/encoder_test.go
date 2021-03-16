package encoder

import (
	"bytes"
	"encoding/binary"
	"eveex/pkg/image"
	"testing"
)

func assertEqual(t *testing.T, variable interface{}, expected interface{}) {
	if variable != expected {
		t.Errorf("AssertEqual mismatch - Expected: %+v, Got: %+v\n", expected, variable)
	}
}

func assertNotEqual(t *testing.T, variable interface{}, notExpected interface{}) {
	if variable == notExpected {
		t.Errorf("AssertNotEqual mismatch - Not wanted: %+v, Got: %+v\n", notExpected, variable)
	}
}

func TestRLEPair(t *testing.T) {
	pair := RLEPair{
		NbZeros: 5,
		Value:   124.5,
	}

	assertEqual(t, pair.NbZeros, uint32(5))
	assertEqual(t, pair.Value, 124.5)
	assertEqual(t, pair.ToString(), "5;124.50")
}

func TestBitstream(t *testing.T) {
	data := []byte{1, 0, 1, 0}
	bs := Bitstream{
		size: 5,
		body: data,
	}

	assertEqual(t, bs.size, 5)
	assertEqual(t, len(bs.GetBody()), len(data))

	bs = *NewEmptyBitstream()
	assertEqual(t, bs.size, 0)
	assertEqual(t, len(bs.GetBody()), 0)

	bs = *NewBitstreamWithSize(5)
	assertEqual(t, bs.size, 5)


	bRes := make([]byte, 2)
	binary.LittleEndian.PutUint16(bRes, uint16(42))
	t.Log(bRes)
	exp := []byte{42, 0}
	result := bytes.Equal(bRes, exp)
	assertEqual(t, result, true)
}

func TestToYUVImage(t *testing.T) {
	img := image.NewEmptyImage(20, 20, 3)
	img.InitEmptyPixels()
	yuv := ToYUVImage(img)

	assertEqual(t, yuv.GetChannels(), img.GetChannels())
	assertEqual(t, yuv.GetWidth(), img.GetWidth())
	assertEqual(t, yuv.GetHeight(), img.GetHeight())
}

func TestSplitInMacroblocs(t *testing.T) {
	img := image.NewEmptyImage(20, 20, 3)
	img.InitEmptyPixels()

	macroblocs := SplitInMacroblocs(*img, 5)
	assertEqual(t, len(macroblocs), 16)
	assertEqual(t, macroblocs[0].GetWidth(), 5)
	assertEqual(t, macroblocs[0].GetHeight(), 5)
}

func TestDCT(t *testing.T) {
	img, err := image.LoadImageFromFile("../../assets/20px.png")
	assertEqual(t, err, nil)

	dctImgR, dctImgG, dctImgB := DCT(*img)
	assertEqual(t, len(dctImgR), img.GetHeight())
	assertEqual(t, len(dctImgR[0]), img.GetWidth())
	assertEqual(t, len(dctImgG), img.GetHeight())
	assertEqual(t, len(dctImgG[0]), img.GetWidth())
	assertEqual(t, len(dctImgB), img.GetHeight())
	assertEqual(t, len(dctImgB[0]), img.GetWidth())
}

func TestZigzagLinearisation(t *testing.T) {
	img, err := image.LoadImageFromFile("../../assets/20px.png")
	assertEqual(t, err, nil)
	dctImgR, _, _ := DCT(*img)
	zigzag := ZigzagLinearisation(dctImgR)

	assertEqual(t, len(zigzag), len(dctImgR) * len(dctImgR[0]))
}

func TestQuantization(t *testing.T) {
	list := []float64{1, 2, 5, 1, 2}
	quant := Quantization(list, 2)

	assertEqual(t, quant[0], 0.0)
	assertEqual(t, quant[1], 0.0)
	assertEqual(t, quant[2], 5.0)
}

func TestRunLevel(t *testing.T) {
	data := []float64{0, 0, 0, 0, 1, 0, 0, 1}
	rle := RunLevel(data)

	t.Log(rle)

	assertEqual(t, len(rle), 2)
	assertEqual(t, rle[0].NbZeros, uint32(4))
	assertEqual(t, rle[0].Value, float64(1))
	assertEqual(t, rle[1].NbZeros, uint32(2))
	assertEqual(t, rle[1].Value, float64(1))
}

func TestEncodePairs(t *testing.T) {
	symbols := map[string][]byte{"0;1.00": {0, 1}, "5;142.50": {1, 1}}
	pairs := []RLEPair{{0, 1.0}, {5, 142.5}}

	bs := EncodePairs(pairs, symbols)
	assertEqual(t, bs.GetBody()[0], byte(0))
	assertEqual(t, bs.GetBody()[1], byte(1))
	assertEqual(t, bs.GetBody()[2], byte(1))
	assertEqual(t, bs.GetBody()[3], byte(1))
}