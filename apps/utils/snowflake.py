# Twitter's Snowflake algorithm implementation which is used to generate distributed IDs.
# https://github.com/twitter-archive/snowflake/blob/snowflake-2010/src/main/scala/com/twitter/service/snowflake/IdWorker.scala

from random import randint
import time
from server.settings import SNOW_DATACENTER_ID


class InvalidSystemClock(Exception):
    """
    时钟回拨异常
    """
    pass


class Constant(object):
    # 64位ID的划分
    WORKER_ID_BITS = 6
    DATACENTER_ID_BITS = 5
    SEQUENCE_BITS = 12

    # 最大取值计算
    MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 2**5-1 0b11111
    MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)

    # 移位偏移计算
    WOKER_ID_SHIFT = SEQUENCE_BITS
    DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

    # 序号循环掩码
    SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

    # Twitter元年时间戳
    TWEPOCH = 1288834974657


class IdWorker(object):
    """
    用于生成IDs
    """

    def __init__(self, datacenter_id, worker_id, sequence=0):
        """
        初始化
        :param datacenter_id: 数据中心（机器区域）ID
        :param worker_id: 机器ID
        :param sequence: 起始序号
        """
        # sanity check
        if worker_id > Constant.MAX_WORKER_ID or worker_id < 0:
            raise ValueError('worker_id值越界')

        if datacenter_id > Constant.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError('datacenter_id值越界')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence

        self.last_timestamp = -1  # 上次计算的时间戳

    def _gen_timestamp(self):
        """
        生成整数时间戳
        :return:int timestamp
        """
        return int(time.time() * 1000)

    def get_id(self):
        """
        获取新ID
        :return:
        """
        timestamp = self._gen_timestamp()

        # 时钟回拨
        if timestamp < self.last_timestamp:
            raise InvalidSystemClock

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & Constant.SEQUENCE_MASK
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = ((timestamp - Constant.TWEPOCH) << Constant.TIMESTAMP_LEFT_SHIFT
                  ) | (self.datacenter_id << Constant.DATACENTER_ID_SHIFT) | \
            (self.worker_id << Constant.WOKER_ID_SHIFT) | self.sequence
        return new_id

    def _til_next_millis(self, last_timestamp):
        """
        等到下一毫秒
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp


idWorker = IdWorker(SNOW_DATACENTER_ID, randint(1, 60))

if __name__ == '__main__':
    print(idWorker.get_id())
