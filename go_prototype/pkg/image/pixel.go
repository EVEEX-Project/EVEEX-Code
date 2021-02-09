package image

import (
	"image"
)

// Pixel contains the data of an image
// It is the same structure for a jpeg and png image
type Pixel struct {
	R int
	G int
	B int
	A int
}

// GetPixels returns an 2D-array of pixels from an image
func GetPixels(img image.Image) ([][]Pixel, error) {
	// getting the bounds of the image
	bounds := img.Bounds()
	width, height := bounds.Max.X, bounds.Max.Y

	var pixels [][]Pixel
	// iteration of the pixels
	for y := 0; y < height; y++ {
		var row []Pixel
		for x := 0; x < width; x++ {
			row = append(row, rgbaToPixel(img.At(x, y).RGBA()))
		}
		pixels = append(pixels, row)
	}

	// returnin the pixels without an error
	return pixels, nil
}

// rgbaToPixel converts values into a Pixel object
func rgbaToPixel(r uint32, g uint32, b uint32, a uint32) Pixel {
	return Pixel{int(r >> 8), int(g >> 8), int(b >> 8), int(a >> 8)}
}