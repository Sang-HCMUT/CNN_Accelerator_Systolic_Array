import sys

if len(sys.argv) < 3:
    print("Usage: python bin2hex.py <input.bin> <output.hex>")
    sys.exit(1)

bin_file = sys.argv[1]
hex_file = sys.argv[2]

with open(bin_file, "rb") as f:
    data = f.read()

# Pad to multiple of 4 bytes
if len(data) % 4 != 0:
    data += b"\x00" * (4 - (len(data) % 4))

with open(hex_file, "w", encoding="utf-8") as f:
    for i in range(0, len(data), 4):
        # Little-endian 32-bit word
        word = int.from_bytes(data[i:i+4], byteorder="little")
        f.write(f"{word:08x}\n")

print(f"[bin2hex] Converted {len(data)} bytes to {len(data)//4} 32-bit hex words.")
