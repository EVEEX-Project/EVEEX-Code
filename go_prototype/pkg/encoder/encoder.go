package encoder

import (
	"eveex/pkg/image"
	"github.com/rs/zerolog/log"
	"math"
)

// ToYUVImage returns an image in the YUV representation
// from an image in the RGB representation
func ToYUVImage(img image.Image) image.Image {
	var yuvPixels [][]image.Pixel
	rgbPixels := img.GetPixels()

	for i := 0; i < img.GetHeight(); i++ {
		var row []image.Pixel
		for j := 0; j < img.GetWidth(); j++ {
			rgbPix := (*rgbPixels)[i][j]
			row = append(row, image.Pixel{
				R: int(0.299 * float64(rgbPix.R) + 0.587 * float64(rgbPix.G) + 0.114 * float64(rgbPix.B)),
				G: int(-0.147 * float64(rgbPix.R) + -0.289 * float64(rgbPix.G) + 0.436 * float64(rgbPix.B)),
				B: int(0.615 * float64(rgbPix.R) + -0.515 * float64(rgbPix.G) + -0.100 * float64(rgbPix.B)),
				A: rgbPix.A,
			})
		}
		yuvPixels = append(yuvPixels, row)
	}

	yuvImg := image.NewEmptyImage(img.GetWidth(), img.GetHeight(), img.GetChannels())
	yuvImg.SetPixels(yuvPixels)
	return yuvImg
}

// SplitInMacroblocs splits an image into square macroblocs
// of side 'size'. The provided image needs to be a multiple
// of the size requested
func SplitInMacroblocs(img image.Image, size int) []image.Image {
	if img.GetWidth() % size != 0 || img.GetHeight() % size != 0 {
		log.Fatal().
			Int("macrobloc_size", size).
			Int("img_height", img.GetHeight()).
			Int("img_width", img.GetWidth()).
			Msg("image size is not a multiple of size, cannot split in macroblocs")
	}

	// getting the number of macroblocs per line/col
	widthMB := img.GetWidth() / size
	heightMB := img.GetHeight() / size

	// creating the list
	list := make([]image.Image, widthMB * heightMB)

	// populating the list with macroblocs
	for k := 0; k < widthMB * heightMB; k++ {
		newBlock := image.NewEmptyImage(size, size, img.GetChannels())
		newBlock.InitEmptyPixels()
		list = append(list, newBlock)
	}

	// distributing the pixels into the macroblocs
	for i := 0; i < img.GetHeight(); i++ {
		for j := 0; j < img.GetWidth(); j++ {
			blockId := j / size + (i / size) * widthMB

			// getting the position of the pixel inside the macrobloc
			mbLine := i - (blockId / widthMB) * size
			mbCol := j - (blockId % widthMB) * size

			// updating the pixel
			list[blockId].SetPixel(mbLine, mbCol, img.GetPixel(i, j))
		}
	}

	log.Debug().
		Int("nb_macroblocs", widthMB * heightMB).
		Int("size", size).
		Msg("Splitted image into macroblocs")

	return list
}

// DCT computes the Discrete Cosine Transform of an image
// the result is a 2D slice of coefficients
func DCT(macrob image.Image) ([][]float64, [][]float64, [][]float64) {
	// creating the final slices
	rCoeffs := make([][]float64, macrob.GetHeight())
	gCoeffs := make([][]float64, macrob.GetHeight())
	bCoeffs := make([][]float64, macrob.GetHeight())
	for k := 0; k < macrob.GetHeight(); k++ {
		rCoeffs[k] = make([]float64, macrob.GetWidth())
		gCoeffs[k] = make([]float64, macrob.GetWidth())
		bCoeffs[k] = make([]float64, macrob.GetWidth())
	}

	// iteration over the macrobloc pixels
	for i := 0; i < macrob.GetHeight(); i++ {
		for j := 0; j < macrob.GetWidth(); j++ {

			for sLine := 0; sLine < macrob.GetHeight(); sLine++ {
				for sCol := 0; sCol < macrob.GetWidth(); sCol++ {
					coeff := math.Cos((math.Pi * float64(sCol) + 0.5) * float64(j)) / float64(macrob.GetWidth()) *
						math.Cos((math.Pi * (float64(sLine) + 0.5) * float64(i)) / float64(macrob.GetHeight()))
					rCoeffs[i][j] += float64(macrob.GetPixel(i, j).R) * coeff
					gCoeffs[i][j] += float64(macrob.GetPixel(i, j).G) * coeff
					bCoeffs[i][j] += float64(macrob.GetPixel(i, j).B) * coeff
				}
			}

			mCol := 1.0
			if j == 0 {
				mCol = 1 / math.Sqrt2
			}

			mLine := 1.0
			if j == 0 {
				mLine = 1 / math.Sqrt2
			}

			rCoeffs[i][j] *= mCol * mLine * 0.25
			gCoeffs[i][j] *= mCol * mLine * 0.25
			bCoeffs[i][j] *= mCol * mLine * 0.25
		}
	}

	return rCoeffs, gCoeffs, bCoeffs
}

// ZigzagLinearisation takes a 2D slice and returns a 1D slice
// of coefficients following a zigzag pattern
func ZigzagLinearisation(coeffs [][]float64) []float64 {
	var zzcoeffs []float64

	return zzcoeffs
}

// Quantization filters the coefficients based on their value
// if a value is below a threshold, the value is replaced by a 0
func Quantization(coeffs []float64, threshold float64) []float64 {
	res := make([]float64, len(coeffs))

	// iteration over the list of coefficients
	for idx, val := range coeffs {
		// if the value is below the threshold, make it 0
		if val <= threshold {
			res[idx] = 0.0
		} else {
			res[idx] = val
		}
	}

	return res
}

// RLEPair contains the data associated
// to a RLE pair
type RLEPair struct {
	nbZeros int
	value float64
}

// RunLevel takes a slice of coefficients and returns
// pairs of value in format (x, y) where x is the number
// of 0 before the value and y is the value
func RunLevel(coeffs []float64) []RLEPair {
	var res []RLEPair

	// iterating over the elements
	var c int
	for _, val := range coeffs {
		// if there is something else than a 0
		if val != 0 {
			pair := RLEPair{nbZeros: c, value: val}
			res = append(res, pair)
			c = 0
		} else {
			c++
		}
	}

	// don't forget the last value event if it is a 0
	pair := RLEPair{nbZeros: c, value: coeffs[len(coeffs)-1]}
	res = append(res, pair)

	return res
}