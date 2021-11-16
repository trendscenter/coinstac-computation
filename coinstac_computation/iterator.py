class Iterator(StopIteration):
    def __init__(self, cache=None, start=0, end=1, step=1):
        self._id = ''
        self.cache = cache
        self.out = {}
        self.reversed = reversed

        self.begin = start
        if cache.get(f"ITERATOR:{self._id}"):
            self.begin = cache[f"ITERATOR:{self._id}"]['begin']

        self.end = end
        if cache.get(f"ITERATOR:{self._id}"):
            self.end = cache[f"ITERATOR:{self._id}"]['end']

        self.step = step
        if cache.get(f"ITERATOR:{self._id}"):
            self.step = cache[f"ITERATOR:{self._id}"]['step']

        self.i = start
        if cache.get(f"ITERATOR:{self._id}"):
            self.i = cache[f"ITERATOR:{self._id}"]['i']

        assert step != 0, "Step size should not be zero."

        if step > 0:
            assert start < end, f"Invalid Start:{start}, End:{end}, Step:{step}"

        if step < 0:
            assert start > end, f"Invalid Start:{start}, End:{end}, Step:{step}"

    def reset(self, begin=0, step=1):
        self.begin = begin
        self.step = step
        self.i = begin

    def _step(self):
        step = {"stop": False}

        if self.step > 0 and self.i + self.step >= self.end:
            step["stop"] = True

        if self.step < 0 and self.i - self.step <= self.end:
            step["stop"] = True

        if not step['stop']:
            if self.step > 0:
                self.i += self.step
            else:
                self.i -= self.step

        return step

    def __iter__(self):
        return self

    def __next__(self):

        if self.cache.get(f'ITERATOR:{self._id}', {}).get('stop'):
            raise StopIteration

        iterator = {
            "begin": self.begin,
            "end": self.end,
            "step": self.step,
            'iter': self.i
        }
        iterator.update(**self._step())

        self.out[f'ITERATOR:{self._id}'] = iterator
        self.cache[f'ITERATOR:{self._id}'] = iterator
        return iterator

#
# cache = {}
# itr = Iterator(cache, 0, 1, 1)
# for i in itr:
#     print(i)
