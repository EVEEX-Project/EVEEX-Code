echo "==> Building go executable"
GOOS=linux GOARCH=riscv64 go build -tags k210 -o eveex_riscv
echo "==> Converting to binary data"
objcopy -I elf64-little -O binary eveex_riscv eveex_riscv.bin
echo "==> Programming the card"
kflash -p /dev/ttyUSB0 -b 750000 -B bit_mic eveex_riscv.bin
