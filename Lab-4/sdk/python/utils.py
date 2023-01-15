def ip_to_bytes(ip):
    splits = ip.split('.')
    return int(splits[0]).to_bytes(1, 'big') + int(splits[1]).to_bytes(1, 'big') + int(splits[2]).to_bytes(1, 'big') + int(splits[3]).to_bytes(1, 'big')

def gen_checksum(data: bytes, chunksize=2):
    # if len(data) % chunksize != 0:
    #     data += b'\x00' * (chunksize - len(data) % chunksize)
    checksum = 0
    for i in range(0, len(data), chunksize):
        checksum += int.from_bytes(data[i:i+chunksize], byteorder='big')
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = ~checksum & 0xffff
    return checksum
