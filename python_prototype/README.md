# EVEEX - Experimental Video Encoder ENSTA Bretagne

<center>

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/EVEEX-Project/EVEEX-Code/graphs/commit-activity) [![GitHub issues](https://img.shields.io/github/issues/EVEEX-Project/EVEEX-Code.svg)](https://github.com/EVEEX-Project/EVEEX-Code/issues/)  [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love png1](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)

</center>

## Introduction

This project is maintained and currently developed by a team of 5 students at ENSTA Bretagne.  
This project is a proof of concept (POC) for the whole project that consist in making a embedded video encoder and decoder on two different FPGA. The end goal is to have a first FPGA with a camera attached that compresses the video flux and send it to another FPGA that can decode the data and show the content on a screen.

## Features

* Generate test images from a json description file (WIP)
* Encode an image to a Bitstream
* Decode a Bitstream into an image (WIP)
* Send Bitstreams from a client to another

## Installation

Before you begin, make sure you have a minimal python 3.8 installation on your system. 

The first step is to clone the project and go into the project's folder.

``` bash
git clone https://github.com/EVEEX-Project/EVEEX-Code.git
cd EVEEX-Code/python_prototype
```

The next step is to make sure you have all requirements already installed. You will need the `pip` tool that is often already installed with python (if not please [check the documentation](https://docs.python.org/3.8/installing/index.html) for the extra steps).

``` bash
python -m pip install -r requirements.txt
```

This line will install every requirements in the text file in order to be able to launch the project.

## Usage

By simply typing `python eveex.py` you will be greeted with an helper message letting you know which command is available.

### Image generation from JSON

There is an option to generate a blank image or a mosaic image with the tools provided. We went one step further and created a way to generate our own test images from a JSON file.

To do so you need to create a description JSON file with the following starting content.

``` JSON
{
  "header" : {
    "size" : [100, 100],
    "background_color": "black"
  },
  "content" : []
}
```

This code will create an image of size 100 by 100 pixels with a black background color. You may notice the empty array named "content". This array will contain every object that should appear on the image.

> Please note that in order to be drawn on the canvas, a shape cannot overflow the canevas

For example if we want to put a red rectangle on the canevas, we have to add the following code into the content array.

``` JSON
{
    "type" : "rectangle",
    "position" : [10, 20],
    "size" : [20, 20],
    "color" : "red"
}
```

The required arguments are the shape's type, the position of the top-left corner, the size of the rectangle and it's colour.

If we want to draw a green circle we need to add the following to the array.

``` JSON
{
    "type" : "circle",
    "position" : [80, 10],
    "size" : 4,
    "color" : "green"
}
```

With a bit of tinkering one can generate complex shapes and great test images for the encoder like the following example.

<center>

![Test image](assets/image_res.png)


</center>

### Encoding an image

One can generate an image from a JSON description file for example. Let's save this image as `test.png`.

In order to encode the image and save it as a bitstream file called `bitstream.txt` one can use the following command.

``` bash
python eveex.py -e test.png bitstream.txt
```