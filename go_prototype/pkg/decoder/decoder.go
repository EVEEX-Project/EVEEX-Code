package decoder

import (
	"eveex/pkg/encoder"
	"eveex/pkg/image"
	"math"
)

func BitstreamToRLE(stream encoder.Bitstream, symbols map[string]string) []*encoder.RLEPair {
	var pairs []*encoder.RLEPair
	var buffer = make([]byte, 100)

	for _, val := range stream.GetBody() {
		buffer = append(buffer, val)
		if val, ok := symbols[string(buffer)]; ok {
			pair := encoder.RLEPairFromString(val)
			pairs = append(pairs, pair)
		}
	}

	return pairs
}

func RunLength(pairs []*encoder.RLEPair) []float64 {
	var res []float64

	for _, pair := range pairs {
		for k := 0; k < pair.NbZeros; k++ {
			res = append(res, 0)
		}
		res = append(res, pair.Value)
	}

	return res
}

func ZigZag(coeffsRGB []float64) ([][]float64, [][]float64, [][]float64) {
	var length int
	length = len(coeffsRGB) / 3
	coeffsR := coeffsRGB[:length]
	coeffsG := coeffsRGB[length:2*length]
	coeffsB := coeffsRGB[2*length:]

	n := int(math.Sqrt(float64(len(coeffsR))))

	var resR = make([][]float64, n)
	var resG = make([][]float64, n)
	var resB = make([][]float64, n)
	for k := 0; k < n; k++ {
		resR[k] = make([]float64, n)
		resG[k] = make([]float64, n)
		resB[k] = make([]float64, n)
	}

	var up = false
	var i, j = 0, 0
	for k := 0; k < len(coeffsR); k++ {
		// adding the current point
		resR[i][j] = coeffsR[k]
		resG[i][j] = coeffsG[k]
		resB[i][j] = coeffsB[k]

		// if we are going up
		if up {
			if j == (n-1) {
				i++
				up = false // changing direction
			} else if i == 0 {
				j++
				up = false // changing direction
			} else {
				// on the diag
				i--
				j++
			}
		} else {
			if i == (n-1) {
				j++
				up = true // changing direction
			} else if j == 0 {
				i++
				up = true // changing direction
			} else {
				// on the diag
				j--
				i++
			}
		}
	}

	return resR, resG, resB
}

func InverseDCT(coeffsR [][]float64, coeffsG [][]float64, coeffsB [][]float64) *image.Image{
	var res = image.NewEmptyImage(len(coeffsR), len(coeffsR[0]), 3)
	res.InitEmptyPixels()

	for i := 0; i < res.GetHeight(); i++ {
		for j := 0; j < res.GetWidth(); j++ {
			var tmpR, tmpG, tmpB float64
			pix := res.GetPixel(i, j)

			// double sum
			for sLine := 0; sLine < res.GetHeight(); sLine++ {
				for sCol := 0; sCol < res.GetWidth(); sCol++ {
					coef := encoder.FastCos((float64(sCol) * math.Pi * (float64(j) + 0.5)) / float64(res.GetWidth())) *
						encoder.FastCos((float64(sLine) * math.Pi * (float64(i) + 0.5)) / float64(res.GetHeight()))
					tmpR += coeffsR[i][j] * coef
					tmpG += coeffsG[i][j] * coef
					tmpB += coeffsB[i][j] * coef

					// orthogonal factors
					mCol := 1.0
					if i == 0 {
						mCol = 1 / math.Sqrt2
					}

					mLine := 1.0
					if j == 0 {
						mLine = 1 / math.Sqrt2
					}

					pix.R += int(coeffsR[i][j] * mCol * mLine * coef)
					pix.G += int(coeffsG[i][j] * mCol * mLine * coef)
					pix.B += int(coeffsB[i][j] * mCol * mLine * coef)
				}
			}
			tmpR *= 0.25
			tmpG *= 0.25
			tmpB *= 0.25

			// TODO: Check formula, maybe errors
			pix.R += int(tmpR + 0.5)
			pix.G += int(tmpG + 0.5)
			pix.B += int(tmpB + 0.5)
			res.SetPixel(i, j, pix)
		}
	}

	return res
}

func YUVtoRGB(origin *image.Image) *image.Image {
	pixels := *origin.GetPixels()

	// converting each pixel
	for i := 0; i < len(pixels); i++ {
		for j := 0; j < len(pixels[i]); j++ {
			pixels[i][j].YUVToRGB()
		}
	}

	res := image.NewEmptyImage(origin.GetWidth(), origin.GetHeight(), origin.GetChannels())
	res.SetPixels(pixels)
	return res
}

func AssembleMacroblocs(macroblocs []*image.Image, macroblocSize int, width int, height int) *image.Image {
	fullWidth, fullHeight := macroblocSize * width, macroblocSize * height
	res := image.NewEmptyImage(fullWidth, fullHeight, 3)
	res.InitEmptyPixels()

	// for each macrobloc
	for idx, mb := range macroblocs {
		// getting the start position
		i0 := (idx % width) * macroblocSize
		j0 := (idx / width) * macroblocSize

		// updating the pixels
		for i := 0; i < macroblocSize; i++ {
			for j := 0; j < macroblocSize; j++ {
				res.SetPixel(i + i0, j + j0, mb.GetPixel(i, j))
			}
		}
	}

	return res
}