from sys import argv
from os.path import exists
from numpy import array, empty, arange;
from secrets import SystemRandom
from hashlib import sha3_512, sha3_384, sha3_256, sha3_224

def make_array():
    return arange(16, dtype=int)
    systemRandom = SystemRandom()
    return array([systemRandom.randrange(16) for x in range(16)], dtype=int)

def convert_key(key):
    key_encoded = key.encode()
    sha224 = sha3_224(key_encoded).hexdigest()
    sha256 = sha3_256(key_encoded).hexdigest()
    sha384 = sha3_384(key_encoded).hexdigest()
    sha512 = sha3_512(key_encoded).hexdigest()
    return int(sha512 + sha384 + sha256 + sha224 + sha384[:76], 16)

def make_key_tables(key):
    in_table = arange(256, dtype=int)
    for i in range(256, 0, -1):
        in_table[i-1], in_table[key%i] = in_table[key%i], in_table[i-1]
        key//=i
    out_table = empty(256, dtype=int)
    for i in range(256):
        out_table[in_table[i]] = i
    return (in_table, out_table)



def joker(path, key):
    if not exists(path):
        print(f"Couldn't open the file {path}")
        return 0
    upper_array, lower_array = make_array(), make_array()
    key = convert_key(key)
    in_table, out_table = make_key_tables(key)
    with open(path, "rb") as f_in:
        with open(path+'.jokered', "wb") as f_out:
            for i in range(16):
                f_out.write(b'\x00') #write init empty bytes

            new_upper, new_lower = upper_array[15], lower_array[15]

            while read_byte := f_in.read(1):
                read_byte = in_table[int.from_bytes(read_byte)] #convert read byte into int and swap it with one from table

                old_upper, old_lower = new_upper, new_lower #pass new bytes to old ones
                new_upper, new_lower = read_byte//16, read_byte%16 #create new bytes

                upper_array[old_upper], new_upper = new_upper, upper_array[old_upper]
                lower_array[old_lower], new_lower = new_lower, lower_array[old_lower]

                f_out.write(int(out_table[new_upper*16 + new_lower]).to_bytes())
                print(int(out_table[new_upper*16 + new_lower]), end=' ')
            
            f_out.seek(0)

            for i in range(16):
                f_out.write(int(out_table[upper_array[i]*16 + lower_array[i]]).to_bytes())
                print(int(out_table[upper_array[i]*16 + lower_array[i]]), end=' ')

if __name__ == "__main__":
    temp = len(argv)
    if temp == 1:
        print("No path to file given")
    elif temp == 2:
        print("No key given")
    elif temp == 4:
        print("Too many arguments given")
    else:
        joker(argv[1], argv[2])
