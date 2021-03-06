# -*- coding:utf-8 -*-

# ==============================================================================
# 测试collections的相关方法。
# ==============================================================================
import time
import sys
from collections import namedtuple, deque, defaultdict, OrderedDict, Counter
from util.log_util import LoggerUtil

# 日志器
common_logger = LoggerUtil.get_common_logger()

default_time_format = '%Y-%m-%d %H:%M:%S'


def test_namedtuple():
    """
    测试namedtuple。
    :return:
    """
    # namedtuple是一个函数，它用来创建一个自定义的tuple对象。
    # 并且规定了tuple元素的个数，可以用属性而不是索引来引用tuple的某个元素。
    Point = namedtuple('Point', ['x', 'y'])
    point = Point(1, 2)
    common_logger.info("Point:{0}, p.x={1}, p.y={2}.".format(point, point.x, point.y))
    common_logger.info("is Point:{}".format(isinstance(point, Point)))
    common_logger.info("is tuple:{}".format(isinstance(point, tuple)))


def test_dequeue():
    """
    测试dequeue的方法。
    :return:
    """
    q = deque(['a', 'b', 'c'])
    q.append('x')
    q.appendleft('y')
    common_logger.info("DeQueue:".format(q))

    # rotate旋转
    q = deque(range(0, 10))
    for i in range(0, 10):
        q.rotate(1)
        common_logger.info("{0}: {1}".format(i, q))

    q = deque(range(0, 10))
    for i in range(0, 10):
        q.rotate(i)
        common_logger.info("{0}: {1}".format(i, q))

    # 走马灯
    fancy_loading = deque('>-------Hello-------------')

    while True:
        common_logger.info('\r{}'.format(''.join(fancy_loading)))
        fancy_loading.rotate(1)
        sys.stdout.flush()
        time.sleep(0.08)


def test_counter():
    """
    测试counter的方法。
    :return:
    """
    count = Counter()
    for ch in 'programming':
        count[ch] += 1
    common_logger.info(count)

    # 频率测试
    s = '''A Counter is a dict subclass for counting hashable objects. It is an unordered collection
        where elements are stored as dictionary keys and their counts are stored as dictionary values.
        Counts are allowed to be any integer value including zero or negative counts.
        The Counter class is similar to bags or multisets in other languages.'''.lower()

    count = Counter(s)
    # 获取出现频率最高的5个字符
    common_logger.info("出现频率最高的5个字符：{0}".format(count.most_common(5)))


def test_ordered_dict():
    """
    测试有序字典OrderedDict。
    :return:
    """
    items = [('a', 1), ('b', 2), ('c', 3)]

    # dict的Key是无序的
    d = dict(items)
    common_logger.info("dict elements:{0}".format(d))

    # OrderedDict的Key是有序的
    od = OrderedDict(items)
    common_logger.info("ordered dict elements:{0}".format(od))

    od = OrderedDict()
    od['z'] = 1
    od['y'] = 2
    od['x'] = 3
    list_dict = list(od.keys()) # 按照插入的Key的顺序返回
    common_logger.info("ordered dict keys:{0}".format(list_dict))


def test_default_dict():
    """
    在使用Python原生的数据结构dict的时候，如果用 d[key] 访问， 当指定的key不存在时，是会抛出KeyError异常的。
    但是，如果使用defaultdict，只要传入一个默认的工厂方法，那么请求一个不存在的key时，
    便会调用这个工厂方法使用其结果来作为这个key的默认值。
    :return:
    """
    dd = defaultdict(lambda: 'N/A')
    dd['key1'] = 'abc'
    common_logger.info("key1:".format(dd['key1']))
    common_logger.info("key2:".format(dd['key2']))


class Missing(dict):
    def __missing__(self, key):
        return 'missing_value'


class MissingCount(dict):
    def __missing__(self, key):
        return 0


def test_dict_method():
    """
    测试dict的方法。
    :return:
    """
    strings = ('puppy', 'kitten', 'puppy', 'puppy',
               'weasel', 'puppy', 'kitten', 'puppy')
    counts = {}

    # 1. 直接用元素运算
    # try:
    #     for kw in strings:
    #         counts[kw] += 1
    # except KeyError as err:
    #     common_logger.info("出现异常！", err)

    # 2. 预先判断是否有元素
    for kw in strings:
        if kw not in counts:
            counts[kw] = 1
        else:
            counts[kw] += 1
    common_logger.info(counts)

    # 3. 使用setdefault()
    for kw in strings:
        counts.setdefault(kw, 0)
        counts[kw] += 1
    common_logger.info(counts)

    # 4. 使用__missing__
    counts = MissingCount()
    for kw in strings:
        counts[kw] += 1
    common_logger.info(counts)


if __name__ == "__main__":
    pass
    # test_namedtuple()
    # test_dequeue()
    # test_counter()
    # test_ordered_dict()
    # test_default_dict()
    test_dict_method()
