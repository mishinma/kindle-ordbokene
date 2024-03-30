
# start the vm
lxc start win11 --console=vga

# Copy file to the vm
scp dev/ordbokene/kindle_dictionary.zip  Mishi@10.136.43.16:C:\\Users\\Mishi\\Downloads

from vm
scp -T Mishi@10.136.43.16:C:\\Users\\Mishi\\Downloads\\ordbokene.mobi Downloads/ordbokene.mobi

# Kindle Previewer
 - Open it up and click File > Open.
 - Find your dict.opf file and open that.
 - File > Export and export it as a .mobi file.