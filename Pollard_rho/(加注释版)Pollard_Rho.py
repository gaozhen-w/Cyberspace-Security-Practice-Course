from doctest import Example
import random
from numpy import append

def get_num(len):                   #生成一个由用户选择长度的随机数字

    seed = "1234567890"
    str1=[]
    for i in range(len):
        str1.append(random.choice(seed))
    String=''.join(str1)

    return String

def test(num):                      #对相同数字的结果进行比较，验证正确性.

    res1=sm3(num)
    res2=sm3(num)
    print('the test num_ber is:{}'.format(num))
    if res1.result==res2.result:
        print ('By test,two same figures lead to the same results,True!')  
    else:
        print ('By test,two same figures lead to different results,Wrong!') 

def Pollard_Rho(example):
    num = int(example/4)                        # 因为要转化为16进制位数，所以做切割
    x = hex(random.randint(0, 2**(example+1)-1))[2:]
    num_a = sm3(str(x)).result                  # num_a = x_1
    num_b = sm3(num_a).result                   # num_b = x_2
    i = 1
    while num_a[:num] != num_b[:num]:
        num_a = sm3((num_a)).result             # num_a = x_i
        num_b = sm3(sm3(num_b).result).result   # num_b = x_2i
        i=i+1
    num_b = num_a                               # num_b = x_i
    num_a = x                                   # num_a = x
    for j in range(i):
        if sm3(num_a).result[:num] == sm3(num_b).result[:num]:
            return sm3(num_a).result[:num], num_a, num_b
        else:
            num_a = sm3(num_a).result 
            num_b = sm3(num_b).result 

key = [0x3614B2B9,0x5390166F, 0xACD442D7, 0xE38D0600, 
0xA96F30BC, 0x30BC8D06, 0x0FB0EE4D, 0xB0FB3901]

R_key = [0x79cc4519, 0x7a879d8a]

class sm3:

    def __init__(self,str1):
        self.result=self.SM3(str1)
    
    def SM3(self,message):

        m = self.TianChong(message)         # 填充后消息
        M = self.Group(m)                   # 数据分组
        new_iter = self.iteration(M)        # 进行迭代
        res = ''
        for x in new_iter:
                res += hex(x)[2:]
        return res

    def Trresp(self,j):                     #选择加密的密钥
        if j >= 0 and j <= 15:
            return R_key[0]
        else:
            return R_key[1]
    

    def FillF(self,X, Y, Z, j):             #根据选择返回相应的计算结果
        if j >= 0 and j <= 15:
            return X ^ Y ^ Z
        else:
            return ((X & Y) | (X & Z) | (Y & Z))
    
    def GroupG(self,X, Y, Z, j):            #根据选择返回相应的计算结果
        if j >= 0 and j <= 15:
            return X ^ Y ^ Z
        else:
            return ((X & Y) | (~X & Z))


    def TianChong(self,message):            #填充字符串，达到进行加密的要求。

        m = bin(int(message, 16))[2:]
        if len(m) != len(message) * 4:
            m = '0' * (len(message) * 4 - len(m)) + m
        l = len(m)

        l_bin = '0' * (64 - len(bin(l)[2:])) + bin(l)[2:]
        m = m + '1'                         #进行判断，对消息填充后取余或者直接返回。

        if len(m) % 512 > 448:
            m = m + '0' * (512 - len(m) % 512 + 448) + l_bin
        else:
            m = m + '0' * (448 - len(m) % 512) + l_bin
        m = hex(int(m, 2))[2:]
        return m


    def Group(self,m):                      #求得各位序上的结果
        n = len(m) / 128
        M = []
        for i in range(int(n)):
            M.append(m[0 + 128 * i:128 + 128 * i])
        return M

    def get_num(self,X):

        return X ^ self.get_or(X, 15) ^ self.get_or(X, 23)

    def Expand(self,M, n):                 #选择需要的位置对数据进行扩充

        W = []
        W_ = []
        for j in range(16):
            W.append(int(M[n][0 + 8 * j:8 + 8 * j], 16))
        for j in range(16, 68):
            W.append(self.get_num(W[j - 16] ^ W[j - 9] ^ 
            self.get_or(W[j - 3], 15)) ^ self.get_or(W[j - 13], 7) ^ W[j - 6])
        for j in range(64):
            W_.append(W[j] ^ W[j + 4])
        Wstr = ''
        W_str = ''
        for x in W:
            Wstr += (hex(x)[2:] + ' ')
        for x in W_:
            W_str += (hex(x)[2:] + ' ')
        return W, W_

    def get_or(self,X,i):                   #返回两个数据按位或的运算结果
        i = i % 32
        return ((X << i) & 0xFFFFFFFF) | ((X & 0xFFFFFFFF) >> (32 - i))

    def P0(self,X):

        return X ^ self.get_or(X, 9) ^ self.get_or(X, 17)

    def Cross_Func(self,V, M, i):       

        A, B, C, D, E, F, G, H = V[i]
        W, W_ = self.Expand(M, i)
        for j in range(64):

            sh1 = self.get_or((self.get_or(A, 12) + E + 
                self.get_or(self.Trresp(j), j % 32)) % (2 ** 32), 7)

            sh2 = sh1 ^ self.get_or(A, 12)

            test1 = (self.FillF(A, B, C, j) + D + sh2 + W_[j]) % (2 ** 32)

            test2 = (self.GroupG(E, F, G, j) + H + sh1 + W[j]) % (2 ** 32)

            D = C
            C = self.get_or(B, 9)
            B = A
            A = test1
            H = G
            G = self.get_or(F, 19)
            F = E
            E = test2 ^ self.get_or(test2, 9) ^ self.get_or(test2, 17)

        a, b, c, d, e, f, g, h = V[i]
        V_ = [a ^ A, b ^ B, c ^ C, d ^ D, e ^ E, f ^ F, g ^ G, h ^ H]
        return V_

    
    def iteration(self,M):                  #将数据进行迭代处理
        
        n = len(M)
        V = []
        V.append(key)
        for i in range(n):
            V.append(self.Cross_Func(V, M, i))
        return V[n]


if __name__=='__main__':
    gaozhen=12                             #选择碰撞长度为12bit
    formal, m1, m2 = Pollard_Rho(gaozhen)  #得到产生碰撞的12bit的哈希值以及两条信息。
    print("message1:", m1)
    print("message2:", m2)
    print("we can find the collision,and the hex num_ber is:{}".format(formal))