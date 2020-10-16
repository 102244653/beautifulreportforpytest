import os
import time
from datetime import datetime
import allure
from selenium import webdriver
import pytest

from beautifulreportforpytest.beautifulreport import beautiful, CaseResult, BeautifulConfig, BeautifulReport
from src.common.log import Logger
from src.common.small_tools import SmallTool
from src.config.readconfig import data

'''
初始化driver
在执行命令中增加命令行选项
'''
log = Logger().get_logger()
driver = None


@pytest.fixture(scope="session", autouse=True)
def init_report(request):
    """
    测试报告
    :return:
    """
    BeautifulConfig.init_dir()
    beautiful.start_time = int(time.time())
    def makereport():
        myreport = BeautifulReport()
        myreport.report(beautiful=beautiful, description='福乐彩运营管理后台')
        
    request.addfinalizer(makereport)


def make_screen_shot(is_ui=BeautifulConfig.is_ui):
    if is_ui:
        name = datetime.now().strftime('%m%d%H%M%S')
        path_name = u'{}/{}.png'.format(BeautifulConfig.img_path, name)
        global driver
        driver.get_screenshot_as_file(path_name)
        return name


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item):
    """
　　每个测试用例执行后，制作测试报告
　　:param item:测试用例对象
　　:param call:测试用例的测试步骤
            先执行when=’setup’ 返回setup 的执行结果
            然后执行when=’call’ 返回call 的执行结果
            最后执行when=’teardown’返回teardown 的执行结果
　　:return:
　　"""
    # 获取钩子方法的调用结果,返回一个result对象
    outcome = yield
    # 获取调用结果的测试报告，返回一个report对象
    # report对象的属性包括when（steup, call, teardown三个值）、nodeid(测试用例的名字)、outcome(用例的执行结果，passed,failed)
    report = outcome.get_result()

    # 生成beautifulreport报告
    if report.when == "call":
        case_result = CaseResult()
        # result保存每条用例的测试结果
        case_result.className = report.nodeid.split('/')[-1].split('::')[0]
        case_result.methodName = str(item.name)
        case_result.description = str(item.function.__doc__).split(':param')[0]
        case_result.spendTime = str(int(report.duration)) + 's'
        case_result.status = report.outcome
        if report.outcome == 'failed':
            beautiful.failures_case_info.append(str(report.nodeid))
            img = make_screen_shot()
            case_result.log.insert(0, "img=./img/{}.png".format(img))
            case_result.log.append('测试用例执行结果【' + report.outcome + '】:\n' + str(report.longrepr))
        elif report.outcome == 'skipped':
            beautiful.skipped_case_info.append(str(report.nodeid))
            case_result.log.append('测试用例执行结果【' + report.outcome + '】:\n' + str(report.longrepr))
        elif report.outcome == 'passed':
            beautiful.success_case_info.append(str(report.nodeid))
            case_result.log.append('测试用例执行结果【' + report.outcome + '】')
        beautiful.result_list.append(case_result)



