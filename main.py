import zlib
import numpy

amino = ['A', 'C', 'G', 'T']

def convert_to_base_four(number, length):
    result = ""
    for i in range(length):
        x = str(number % 4)
        result = x + result
        number = number // 4
    return result


def make_G_c_th_column(input_length, c):
    p = [i + 1 for i in range(input_length)]
    t = 0
    while 2 ** t - 1 < len(p):
        # print(p)
        p.insert(2 ** t - 1, -(t + 1))
        t += 1
    # print(p)
    p1 = [0 for i in range(len(p))]
    q1 = [0 for i in range(input_length)]
    for i in range(2 ** (c - 1) - 1, len(p), 2 ** c):
        for j in range(2 ** (c - 1)):
            if i + j < len(p):
                p1[i + j] = 1
    for i in range(len(p)):
        if p1[i] == 1 and p[i] > 0:
            q1[p[i] - 1] = 1
    return q1


def make_G_matrix(input_length):
    t = 0
    while 2 ** t - 1 - t <= input_length:
        t += 1
    g_matrix = numpy.identity(input_length)

    for i in range(1, t):
        # print(make_G_c_th_column(input_length, i))
        # print(g_matrix.shape[1])
        # print(type(i), i)
        g_matrix = numpy.insert(g_matrix, g_matrix.shape[1], numpy.array(make_G_c_th_column(input_length, i)), 1)
    return g_matrix


def encode(data_string):
    ascii_codes = [ord(x) for x in data_string]
    # print(ascii_codes)
    base_four_string = ''.join([convert_to_base_four(x, 4) for x in ascii_codes])   # m in documentation
    # print(base_four_string)
    hashed = zlib.crc32(bytes(base_four_string, 'utf-8'))
    # print(hashed)
    # print(convert_to_base_four(hashed, 16), convert_to_base_four(hashed, 16)[10:])
    a_string = base_four_string + convert_to_base_four(hashed, 16)[10:]
    # print(a_string)
    g_matrix = make_G_matrix(len(a_string))
    a_array = numpy.array([int(x) for x in a_string])
    # print(g_matrix)
    b_array = numpy.matmul(a_array, g_matrix)
    b_string = ''.join(str(int(x)%4) for x in b_array)
    # print(b_string)
    parity_quad = sum([int(x) for x in b_string]) % 4
    c_string = str(parity_quad) + b_string
    print(c_string)
    dna_string = [amino[int(x)] for x in c_string]
    return ''.join(dna_string)


def decode(dna_string):
    c_string = ''.join([str(amino.index(x)) for x in dna_string])
    print(c_string)


if __name__ == '__main__':
    dna = encode("hello")
    # print(encode("hello"))
    decode(dna)
    # for i in range(30):
    #     make_G_matrix(i)

    # print(make_G_matrix(15))
    # c = (2, 3)
    # print(c.count(0))
