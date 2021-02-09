package encoder

import (
	"eveex/pkg/image"
	"github.com/rs/zerolog/log"
)

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

func DCT() {

}

func ZigzagLinearisation() {

}

func Quantization() {

}

func RunLevel() {

}