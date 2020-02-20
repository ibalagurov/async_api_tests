import pytest
import sys
import trio
import inspect
import re
import time


pytestmark = pytest.mark.trio
io_test_pattern = re.compile("io_.*")


async def tests(subtests):
    def find_io_tests(subtests, ignored_names):
        functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
        for (f_name, function) in functions:
            if f_name in ignored_names:
                continue
            if re.search(io_test_pattern, f_name):
                yield (run, subtests, f_name, function)

    async def run(subtests, test_name, test_function):
        with subtests.test(msg=test_name):
            await test_function()

    self_name = inspect.currentframe().f_code.co_name
    async with trio.open_nursery() as nursery:
        for io_test in find_io_tests(subtests, {self_name}):
            nursery.start_soon(*io_test)


accepted_error = 0.1


async def io_test_1():
    await assert_sleep_duration_ok(1)


async def io_test_2():
    await assert_sleep_duration_ok(2)


async def io_test_3():
    await assert_sleep_duration_ok(3)


async def io_test_4():
    await assert_sleep_duration_ok(4)


async def assert_sleep_duration_ok(duration):
    start = time.time()
    await trio.sleep(duration)
    actual_duration = time.time() - start
    assert abs(actual_duration - duration) < accepted_error
