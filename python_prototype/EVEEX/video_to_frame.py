import cv2
import logger
import time

def vid2frames(video):
  vidcap = cv2.VideoCapture(video)
  success,image = vidcap.read()
  count = 0
  sortie = []
  while success:
    sortie.append(image)
    success,image = vidcap.read()
    count += 1
  return sortie

def frames2vid(frames):
  height, width, channels = frames[0].shape
  out = cv2.VideoWriter('test2.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))

  for i in range(len(frames)):
    out.write(frames[i])
  out.release()


if __name__ == "__main__":
  frames = vid2frames('assets/video_test.mp4')
  frames2vid(frames)