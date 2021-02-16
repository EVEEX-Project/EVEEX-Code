package image

import "testing"

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

func TestCreatePixel(t *testing.T) {
	pix := Pixel{R: 1, G: 2, B: 3, A: 4}

	if pix.R != 1 || pix.G != 2 || pix.B != 3 || pix.A != 4 {
		t.Error("Error while initializing pixels")
		t.Errorf("%+v\n", pix)
	}
}

func TestCreateImage(t *testing.T) {
	img := Image{
		width:    10,
		height:   20,
		channels: 3,
	}

	assertEqual(t, img.width, 10)
	assertEqual(t, img.height, 20)
	assertEqual(t, img.channels, 3)

	img = *NewEmptyImage(5, 5, 5)

	assertEqual(t, img.width, 5)
	assertEqual(t, img.height, 5)
	assertEqual(t, img.channels, 5)
}

func TestImageGetterSetter(t *testing.T) {
	img := Image{
		width:    10,
		height:   20,
		channels: 3,
	}

	assertEqual(t, img.GetWidth(), 10)
	assertEqual(t, img.GetHeight(), 20)
	assertEqual(t, img.GetChannels(), 3)

	img.SetWidth(5)
	img.SetHeight(15)
	img.SetChannels(20)

	assertEqual(t, img.GetWidth(), 5)
	assertEqual(t, img.GetHeight(), 15)
	assertEqual(t, img.GetChannels(), 20)
}

func TestImagePixels(t *testing.T) {
	img := NewEmptyImage(10, 10, 10)
	img.InitEmptyPixels()

	assertEqual(t, len(*img.GetPixels()), img.GetHeight())

	pix := Pixel{R: 1, G: 2, B: 3, A: 1}
	img.SetPixel(5, 5, pix)

	assertEqual(t, img.GetPixel(5, 5), pix)

	pixArr := make([][]Pixel, 5)
	for k := range pixArr {
		pixArr[k] = make([]Pixel, 10)
	}
	img.SetPixels(pixArr)
	assertEqual(t, len(*img.GetPixels()), len(pixArr))
}

func TestLoadingImage(t *testing.T) {
	img, err := LoadImageFromFile("../../assets/20px.png")

	if err != nil {
		t.Errorf("Error while opening image : %s\n", err.Error())
	}

	assertNotEqual(t, img, nil)
	assertEqual(t, img.GetChannels(), 4)
}

func TestErrorLoadingImage(t *testing.T) {
	_, err := LoadImageFromFile("dontexist")

	assertNotEqual(t, err, nil)
	assertNotEqual(t, err.Error(), "")
}