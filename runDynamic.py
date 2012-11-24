import usb
import itertools 


XMOS_XTAG2_VID = 0x20b1
XMOS_XTAG2_PID = 0xf7d1
XMOS_XTAG2_EP_IN = 0x82
XMOS_XTAG2_EP_OUT = 0x01

LOADER_BUF_SIZE = 512

loader_cmd_type = dict(zip([
	"LOADER_CMD_NONE",
	"LOADER_CMD_WRITE_MEM",
	"LOADER_CMD_WRITE_MEM_ACK",
	"LOADER_CMD_GET_VERSION",
	"LOADER_CMD_GET_VERSION_ACK",
	"LOADER_CMD_JUMP",
	"LOADER_CMD_JUMP_ACK"], range(6)))

_32to8 = lambda thirtyTwo: [(thirtyTwo >> 24), (thirtyTwo >> 16) & 0xFF, (thirtyTwo >> 8) & 0xFF, (thirtyTwo & 0xFF)]
_32to8 = lambda thirtyTwo: [(thirtyTwo&0xFF), (thirtyTwo >> 8) & 0xFF, (thirtyTwo >> 16) & 0xFF, ( (thirtyTwo >> 24)& 0xFF)]
_flatten = lambda l: list(itertools.chain(*[[x] if type(x) not in [list] else x for x in l]))

def load_firmware(byte_array):
	dev = usb.core.find(idVendor=XMOS_XTAG2_VID, idProduct=XMOS_XTAG2_PID)
	address = 0x10000
	block_size = LOADER_BUF_SIZE - 12
	bin_len = len(byte_array)
	num_blocks = bin_len / block_size
	remainder = bin_len % block_size

	for i in range(num_blocks):
		cmd_buf = []
		cmd_buf += _32to8(loader_cmd_type['LOADER_CMD_WRITE_MEM'])
		cmd_buf += _32to8(address)
		cmd_buf += _32to8(block_size)
		cmd_buf += byte_array[i*block_size:(i+1)*block_size]
		print len(cmd_buf)
		dev.write(XMOS_XTAG2_EP_OUT, cmd_buf, 0, 1000) 
		dev.read(XMOS_XTAG2_EP_IN, 8, 0, 1000) 
		address += block_size

	if remainder:
		cmd_buf = []
		cmd_buf += _32to8(loader_cmd_type['LOADER_CMD_WRITE_MEM'])
		cmd_buf += _32to8(address)
		cmd_buf += _32to8(remainder)
		cmd_buf += byte_array[block_size*num_blocks::]
		dev.write(XMOS_XTAG2_EP_OUT, cmd_buf, 0, 1000) 
		dev.read(XMOS_XTAG2_EP_IN, 8, 0, 1000) 
		address += block_size

	cmd_buf = []
	cmd_buf += _32to8(loader_cmd_type['LOADER_CMD_JUMP'])
	dev.write(XMOS_XTAG2_EP_OUT, cmd_buf, 0, 1000) 
	dev.read(XMOS_XTAG2_EP_IN, 8, 0, 1000)
	dev.reset()

if __name__ == "__main__":
	import app_l1_hid
	load_firmware(_flatten(map(_32to8, app_l1_hid.burnData)))
