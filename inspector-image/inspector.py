#! /usr/bin/env python3

from PIL import Image
from PIL.ExifTags import TAGS
import sys, re


# Possible flags:
# -map: extract GPS coordinates
# -steg: extract PGP key hidden in image
def main():
    # Check sys.args for flag
    args = sys.argv
    if len(args) == 0:
        print("Usage: python extract.py <flag> <image>")
        return
    flag = args[1]
    image = args[2]
    with open(image, "r") as f:
        if f is None:
            print("Image not found")
            return
    if flag != "-map" and flag != "-steg":
        print("Possible flags: -map, -steg")
        return
    if flag == "-map":
        extract_map(image)
    if flag == "-steg":
        extract_steg(image)


def extract_map(image):
    img = Image.open(image)
    exif = img._getexif()
    if exif is None:
        print("No GPS data found")
        return
    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            try:
                print(f"Lat/Lon: ({value[2][0]}) / ({value[4][0]})")
            except:
                print("No valid GPS data found")
            return
    print("No GPS data found")


def extract_steg(image):
    with open(image, "rb") as f:
        start = re.compile(
            rb"-----BEGIN PGP PUBLIC KEY BLOCK-----(.*)-----END PGP PUBLIC KEY BLOCK-----",
            re.DOTALL,
        )
        content = f.read()
        match = start.search(content)
        if match is None:
            print("No PGP key found")
            return
        key = match.group()
        print(key.decode("utf-8"))
        return


if __name__ == "__main__":
    main()