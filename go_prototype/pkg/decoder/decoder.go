package decoder

import (
	"eveex/pkg/encoder"
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

func ZigZag(coeffsRGB []float64) ([][]float64, [][]float64, [][]float64){
	var length int
	length = len(coeffsRGB) / 3
	coeffsR := coeffsRGB[:length]
	coeffsG := coeffsRGB[length:2*length]
	coeffsB := coeffsRGB[2*length:]

	return singleZigZag(coeffsR), singleZigZag(coeffsG), singleZigZag(coeffsB)
}

func singleZigZag(coeffs []float64) [][]float64 {
	n := int(math.Sqrt(float64(len(coeffs))))

	var res = make([][]float64, n)
	for k := 0; k < n; k++ {
		res[k] = make([]float64, n)
	}

	var up = false
	var i, j = 0, 0
	for k := 0; k < len(coeffs); k++ {
		// adding the current point
		if coeffs[k] != 0 {
			res[i][j] = coeffs[k]
		}

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

	return res
}

func DCT() {

}

func YUVtoRGB() {

}

func AssembleMacroblocs() {

}