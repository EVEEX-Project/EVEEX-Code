package image

import (
	"fmt"
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

func (i *Image) GetSize() (int, int) {
	return i.width, i.height
}

func (i *Image) GetChannels() int {
	return i.channels
}

func LoadImageFromFile(filename string) (Image, error) {
	// You can register another format here
	image.RegisterFormat("png", "png", png.Decode, png.DecodeConfig)
	image.RegisterFormat("jpg", "jpg", jpeg.Decode, jpeg.DecodeConfig)
	image.RegisterFormat("jpeg", "jpeg", jpeg.Decode, jpeg.DecodeConfig)

	file, err := os.Open(filename)
	if err != nil {
		return Image{}, fmt.Errorf("error: file could not be opened")
	}
	defer file.Close()

	var res Image
	img, format, err := image.Decode(file)
	if err != nil {
		return Image{}, fmt.Errorf("error: image could not be decoded with format '%s'", format)
	}

	bounds := img.Bounds()
	res.width, res.height = bounds.Max.X, bounds.Max.Y
	res.pixels, err = GetPixels(img)

	if format == "png" {
		res.channels = 4
	} else {
		res.channels = 3
	}

	return res, nil
}