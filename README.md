# Tiny News

## TODO
	- Improve News (offer multiple sources)
	- Unique puzzle every day of the week

## More ideas
- Star chart - what is in the sky tonight - docs.astronomyapi.com/endpoints/studio/star-chart
- fun fact
- quote of the day?

## Things I wrote down when I started that I have since forgotten about...

`sudo nano /etc/udev/rules.d/99-escpos.rules`

Add the following line:

`SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", ATTR{idProduct}=="0e28", MODE="0666", GROUP="plugdev"`


`sudo udevadm control --reload-rules`
`sudo udevadm trigger`

`pip install -U python-escpos[all] --pre`