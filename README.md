# coral-pi

For Raspberry Pi 3B+ and Raspbian Lite 2018-11-13 - https://www.raspberrypi.org/downloads/raspbian/

Prep
1. sudo apt-get update -y && sudo apt-get upgrade -y
2. sudo apt-get install -y feh git python3-pip python3-dev python3-numpy libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev libjpeg-dev libfreetype6-dev python3-setuptools && sudo -H pip3 install wheel && sudo -H pip3 install pygame
3. cd ~ && wget https://dl.google.com/coral/edgetpu_api/edgetpu_api_latest.tar.gz -O edgetpu_api.tar.gz --trust-server-names && tar xzf edgetpu_api.tar.gz && cd edgetpu_api && bash ./install.sh
4. Unplug / reinsert TPU
3. cd ~ && mkdir models && cd models && curl -O https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite && curl -O https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite
4. cd ~ && git clone clone https://github.com/spinoza1791/detection.git
5. cd ~/detection && python3 pi-tpu.py --model=/home/pi/models/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite --dims=320



3. Verify python version: python3 --version (must be Python 3.5.x or higher)
4. Install Pi camera v2.1 - https://www.makeuseof.com/tag/set-up-raspberry-pi-camera-module/
5. echo "bcm2835_v4l2" | sudo tee -a /etc/modules >/dev/null
6. Set Pi memory split to 128 - https://www.raspberrypi.org/documentation/configuration/config-txt/memory.md
7. Reboot

Installation
1. wget http://storage.googleapis.com/cloud-iot-edge-pretrained-models/edgetpu_api.tar.gz
mkdir ~/models
cd ~/models

curl -O https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite 
2. tar xzf edgetpu_api.tar.gz
3. bash ./install.sh - "Would you like to enable the maximum operating frequency?" Answer Y
4. Plug in the Accelerator using the provided USB 3.0 cable. (If you already plugged it in, remove it and replug it so the just-installed udev rule can take effect.)
5. cd python-tflite-source/edgetpu
6. Test installation: 
python3 demo/classify_image.py \
--model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
--label test_data/inat_bird_labels.txt \
--image test_data/parrot.jpg

Results
Ara macao (Scarlet Macaw)
Score :  0.613281

Platycercus elegans (Crimson Rosella)
Score :  0.152344

7. Download Edge TPU models: https://coral.withgoogle.com/models/
   a. MobileNet SSD v2 (Faces)
   b. Input size: 320x320 (Does not require a labels file)
   cd ~/detection && python3 pi-tpu-dev.py --model=~/models/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite --dims=320 --max_obj=10 --thresh=0.6




