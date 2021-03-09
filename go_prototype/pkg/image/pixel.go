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

func (p *Pixel) RGBToYUV() {
	r, g, b := float64(p.R), float64(p.G), float64(p.B)

	y := 0.299 * r + 0.587 * g + 0.114 * b
	u := -0.14713 * r - 0.28886 * g + 0.436 * b
	v := 0.615 * r - 0.51498 * g - 0.10001 * b

	p.R = int(y)
	p.G = int(u)
	p.B = int(v)
}

func (p *Pixel) YUVToRGB() {
	y, u, v := float64(p.R), float64(p.G), float64(p.B)

	r := y + 1.13983 * v
	g := y - 0.39465 * u - 0.5806 * v
	b := y + 2.03211 * u

	p.R = int(r)
	p.G = int(g)
	p.B = int(b)
}