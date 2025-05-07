## TODO

- Figure out what makes a good wordwheel puzzle
	- low scrabble score (very few letters to give away hints)
	- maximizing repeated letters (if letters repeat e.g. ee or ete then they can be read in multiple directions)
	- replacing letters that would give the word away (high value)


More ideas
- Star chart - what is in the sky tonight - docs.astronomyapi.com/endpoints/studio/star-chart
- fun fact
- quote of the day


`sudo nano /etc/udev/rules.d/99-escpos.rules`

Add the following line:

`SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", ATTR{idProduct}=="0e28", MODE="0666", GROUP="plugdev"`


`sudo udevadm control --reload-rules`
`sudo udevadm trigger`

`pip install -U python-escpos[all] --pre`