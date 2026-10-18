# Firmware policy

No proprietary blobs in git, ever. Device firmware (Qualcomm modem, zap shaders,
ath10k board data) is extracted locally from the device (`vendor_a`, modem
partitions) at build time. Each device folder in `devices/<codename>/firmware/`
documents which files are needed, where they come from, and their SHA-256.

Free firmware (ath10k firmware-5.bin, a630_sqe.fw) comes from linux-firmware.
