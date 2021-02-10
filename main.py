import zlib
import numpy
import math
import random

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
    while 2 ** t - 1 - t < input_length:
        t += 1
    g_matrix = numpy.identity(input_length)
    # print(t)
    for i in range(1, t+1):
        # print(make_G_c_th_column(input_length, i))
        # print(g_matrix.shape[1])
        # print(type(i), i)
        g_matrix = numpy.insert(g_matrix, g_matrix.shape[1], numpy.array(make_G_c_th_column(input_length, i)), 1)
    return g_matrix


def encode(data_string):
    ascii_codes = [ord(x) for x in data_string]
    # print(ascii_codes)
    base_four_string = ''.join([convert_to_base_four(x, 4) for x in ascii_codes])  # m in documentation
    # print(base_four_string)
    hashed = zlib.crc32(bytes(base_four_string, 'utf-8'))
    # print(hashed)
    # print(convert_to_base_four(hashed, 16), convert_to_base_four(hashed, 16)[10:])
    a_string = base_four_string + convert_to_base_four(hashed, 16)[10:]
    # print(a_string, " a")
    g_matrix = make_G_matrix(len(a_string))
    a_array = numpy.array([int(x) for x in a_string])
    # print(g_matrix)
    b_array = numpy.matmul(a_array, g_matrix)
    b_string = ''.join(str(int(x) % 4) for x in b_array)
    # print(b_string, " b")
    parity_quad = sum([int(x) for x in b_string]) % 4
    c_string = str(parity_quad) + b_string
    # print(c_string, " c")
    dna_string = [amino[int(x)] for x in c_string]
    return ''.join(dna_string)


def make_H_matrix(input_length):
    t = math.floor(math.log(input_length, 2)) + 1
    A_arr = [make_G_c_th_column(input_length - t, i) for i in range(1, t + 1)]
    A_matrix = numpy.array(A_arr).transpose()
    # print(A_matrix.shape)
    # print(A_matrix)
    h_matrix = numpy.insert(A_matrix, A_matrix.shape[0], numpy.identity(t) * (-1), 0)
    # print(h_matrix)
    return h_matrix


def correct_errors(res_string, error_vector):
    # print(res_string, " res")
    value = -1
    error_location = 0
    for i in range(len(error_vector)):
        if error_vector[i] != 0:
            if value == -1:
                value = error_vector[i]
                error_location += 2 ** i
            elif value != error_vector[i]:
                return -1
            else:
                error_location += 2 ** i

    if value == -1:
        return res_string
    # print(error_location, "loc")
    # print(2 ** (math.floor(math.log(error_location, 2))), "check")
    if error_location == 2 ** (math.floor(math.log(error_location, 2))):
        # print(error_location, "1")
        error_location = math.floor(math.log(error_location, 2))
        # print(error_location, "2")
        # if error_location == 0 :
        error_location = len(res_string) - len(error_vector) + error_location
        # print( res_string, error_location)
        # print(res_string, "***********")
        # c_s = res_string[:error_location] + str((int(res_string[error_location]) - value) % 4) + res_string[error_location + 1:]
        # print(''.join(amino[int(x)] for x in c_s))
        # return res_string
    else:
        t = 0
        while 2 ** t - 1 < error_location:
            t += 1
        error_location -= t + 1
    # print("one error corrected")
    correct_value = (int(res_string[error_location]) - value) % 4
    # print(value, " val")
    # print(error_location, " loc")
    # print(correct_value)
    correct_string = res_string[:error_location] + str(correct_value) + res_string[error_location + 1:]
    # correct_string[error_location] = str(correct_value)
    return correct_string


def convert_to_base_ten(number):
    result = 0
    i = 0
    while number > 0:
        result = result + (number % 10) * 4 ** i
        number = number // 10
        i = i + 1
    return result


def decode(dna_string):
    c_string = ''.join([str(amino.index(x)) for x in dna_string])
    # print(c_string, " c")
    parity_quad = int(c_string[0])
    b_string = c_string[1:]
    # print(b_string, " b")
    h_matrix = make_H_matrix(len(b_string))
    b_array = numpy.array([int(x) for x in b_string])
    # print(numpy.matrix(b_array), numpy.array(h_matrix).shape)
    e_array = numpy.matmul(b_array, h_matrix)
    # print(e_array)
    e_vector = [x % 4 for x in e_array]
    e_string = ''.join([str(int(x) % 4) for x in e_array])
    # print(e_vector)
    t = h_matrix.shape[1]
    # res_string = b_string[:len(b_string)-t]
    # print(res_string)
    correct_string = correct_errors(b_string, e_vector)
    # print(correct_string, "b_1")
    if correct_string == -1:
        return "can't restore : more than one error"
    res_parity = sum([int(x) for x in correct_string]) % 4
    if res_parity != parity_quad:
        return "parity mismatch"

    a_string = correct_string[:len(correct_string) - t]
    m_string = a_string[:len(a_string) - 6]
    crc_string = a_string[len(a_string) - 6:]
    hashed = zlib.crc32(bytes(m_string, 'utf-8'))
    crc_check = convert_to_base_four(hashed, 16)[10:]
    # print(b_string)
    # print(a_string)
    # print(m_string)
    # print(crc_string)
    # print(crc_check)
    if crc_string != crc_check:
        return "crc mismatch"
    m_array = []
    for i in range(0, len(m_string), 4):
        m_array.append(m_string[i:i + 4])
    # print(m_array)
    ascii_array = [convert_to_base_ten(int(x)) for x in m_array]
    # print(ascii_array)
    s_array = [chr(x) for x in ascii_array]
    # print(s_array)

    return ''.join(s_array)


if __name__ == '__main__':
    # print(math.floor(math.log(1, 2)))
    # print("hello"[-2:])
    # t = 0
    # while 2 ** t - 1 - t < 27:
    #     t += 1
    # print(t)
    # print(decode(encode("laproe")))
    testing_string = "la_Project"
    testing_times = 10
    tests_count = 100
    errors_count = 50
    total_fail = 0
    for k in range(testing_times):
        a = []
        for i in range(tests_count):
            a.append([x for x in encode(testing_string)])
        # print(a)
        for j in range(errors_count):
            x = random.randint(0, len(a)-1)
            y = random.randint(0, len(a[0])-1)
            a[x][y] = amino[random.randint(0, 3)]
        for i in range(tests_count):
            string = ''.join(a[i])
            if decode(string) != testing_string:
                total_fail += 1
    print(total_fail/testing_times)