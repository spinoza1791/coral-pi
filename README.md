# coral-pi

For Raspberry Pi 3B+ and Raspbian Lite 2018-11-13 - https://www.raspberrypi.org/downloads/raspbian/

Prep
1. sudo apt-get update -y && sudo apt-get upgrade -y
2. sudo apt-get install feh -y
3. Verify python version: python3 --version
   a. must be Python 3.5.x or higher
4. Install Pi camera v2.1 - https://www.makeuseof.com/tag/set-up-raspberry-pi-camera-module/
5. add to /etc/modules - bcm2835-v4l2
6. Set Pi memory split to 128 - https://www.raspberrypi.org/documentation/configuration/config-txt/memory.md
7. Reboot

Installation
1. wget http://storage.googleapis.com/cloud-iot-edge-pretrained-models/edgetpu_api.tar.gz
2. tar xzf edgetpu_api.tar.gz
3. bash ./install.sh
   a. "Would you like to enable the maximum operating frequency?" Answer: Y
4. Plug in the Accelerator using the provided USB 3.0 cable. (If you already plugged it in, remove it and replug it so the just-installed udev rule can take effect.)
5. cd python-tflite-source/edgetpu
6. Test installation: 
python3 demo/classify_image.py \
--model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
--label test_data/inat_bird_labels.txt \
--image test_data/parrot.jpg

Results
Ara macao (Scarlet Macaw)
"Score :  0.613281"
Platycercus elegans (Crimson Rosella)
"Score :  0.152344"

7. Download Edge TPU models: https://coral.withgoogle.com/models/
   a. MobileNet SSD v2 (Faces)
   b. Input size: 320x320 (Does not require a labels file)



