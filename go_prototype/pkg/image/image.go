package image

import (
	"fmt"
	"github.com/rs/zerolog/log"
	"image"
	"image/jpeg"
	"image/png"
	"os"
)

type Image struct {
	pixels [][]Pixel
	width int
	height int
	channels int
}

// GetHeight returns the height of the image
func (img *Image) GetHeight() int {
	return img.height
}

// SetHeight set the new height of the image
func (img *Image) SetHeight(value int) {
	img.height = value
}

// GetWidth returns the width of the image
func (img *Image) GetWidth() int {
	return img.width
}

// SetWidth set the new width of the image
func (img *Image) SetWidth(value int) {
	img.width = value
}

// GetChannels return the number of channels of the image
func (img *Image) GetChannels() int {
	return img.channels
}

// SetChannels set the new channel number of the image
func (img *Image) SetChannels(value int) {
	img.channels = value
}

// GetPixels returns the pixel array of the image
func (img *Image) GetPixels() *[][]Pixel {
	return &img.pixels
}

// SetPixels sets the new array for the pixels
func (img *Image) SetPixels(value [][]Pixel) {
	img.pixels = value
}

// GetPixel returns a single pixel from the data
func (img *Image) GetPixel(i int, j int) Pixel {
	return img.pixels[i][j]
}

// SetPixel sets a single pixel in the data
func (img *Image) SetPixel(i int, j int, pix Pixel) {
	img.pixels[i][j] = pix
}

// InitEmptyPixels init the pixel 2D-array with default
// pixel data
func (img *Image) InitEmptyPixels() {
	img.pixels = make([][]Pixel, img.height)
	for y := 0; y < img.height; y++ {
		img.pixels[y] = make([]Pixel, img.width)
	}
}

// NewEmptyImage creates an empty image
func NewEmptyImage(width int, height int, channels int) *Image {
	return &Image{
		width: width,
		height: height,
		channels: channels,
	}
}

// LoadImageFromFile tries to load an image from the disk
// and put it in an Image structure
func LoadImageFromFile(filename string) (*Image, error) {
	// Registering detected formats
	image.RegisterFormat("png", "png", png.Decode, png.DecodeConfig)
	image.RegisterFormat("jpg", "jpg", jpeg.Decode, jpeg.DecodeConfig)
	image.RegisterFormat("jpeg", "jpeg", jpeg.Decode, jpeg.DecodeConfig)

	// opening the file
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("error: file could not be opened")
	}
	defer file.Close() // don't forget to close the file at the end

	// decoding the image
	img, format, err := image.Decode(file)
	if err != nil {
		return nil, fmt.Errorf("error: image could not be decoded with format '%s'", format)
	}

	// getting the number of channels
	var channels int
	if format == "png" {
		channels = 4
	} else {
		channels = 3
	}

	// setting up the image parameters
	bounds := img.Bounds()
	res := NewEmptyImage(bounds.Max.X, bounds.Max.Y, channels)
	res.pixels, err = GetPixels(img)

	log.Debug().
		Int("width", res.width).
		Int("height", res.height).
		Int("channels", res.channels).
		Msgf("Loaded an image : %s", filename)

	return res, nil
}