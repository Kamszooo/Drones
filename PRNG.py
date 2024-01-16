class MT19937:
    def __init__(self, seed):
        (self.w, self.n, self.m, self.r) = (32, 624, 397, 31)
        self.a = 0x9908B0DF
        (self.u, self.d) = (11, 0xFFFFFFFF)
        (self.s, self.b) = (7, 0x9D2C5680)
        (self.t, self.c) = (15, 0xEFC60000)
        self.l = 18
        self.f = 1812433253

        # make a arry to store the state of the generator
        self.MT = [0 for _ in range(self.n)]
        self.index = self.n + 1
        self.lower_mask = 0x7FFFFFFF #(1 << r) - 1 // That is, the binary number of r 1's
        self.upper_mask = 0x80000000#lowest w bits of (not lower_mask)

        self.mt_seed(seed)

    # initialize the generator from a seed
    def mt_seed(self, seed):
        self.MT[0] = seed
        for i in range(1, self.n):
            temp = self.f * (self.MT[i - 1] ^ (self.MT[i - 1] >> (self.w - 2))) + i
            self.MT[i] = temp & 0xffffffff

    # Extract a tempered value based on MT[index]
    # calling twist() every n numbers
    def extract_number(self):
        if self.index >= self.n:
            self.twist()
            self.index = 0

        y = self.MT[self.index]
        y = y ^ ((y >> self.u) & self.d)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)

        self.index += 1
        return y & 0xffffffff



    def twist(self):
        for i in range(0, self.n):
            x = (self.MT[i] & self.upper_mask) + (self.MT[(i + 1) % self.n] & self.lower_mask)
            xA = x >> 1
            if (x % 2) != 0:
                xA = xA ^ self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA


    def display_state(self):
        print("Internal State:")
        for i in range(self.n):
            print(f"MT[{i}] = {self.MT[i]}")
        print(f"index = {self.index}")
        print()


if __name__ == '__main__':
    mt19937_instance = MT19937(seed=0xcd7d660bbec1cfe8a72ccb85d218c5f5)

    for _ in range(3):
        print(mt19937_instance.extract_number())
