'''
    创建钩子函数用于对测试失败的用例进行图片截图同时显示在allure报告上；此出的钩子函数是根目录级别

'''

import allure
import pytest

@pytest.hookimpl(tryfirst=True,hookwrapper=True)
# 参数tryfirst是多个钩子函数，该被装饰函数将第一个执行，hookwrapper这是一个钩子包装器，可以控制钩子前后的执行逻辑
# 被装饰函数，每一个测试函数|方法，会自动执行
def pytest_runtest_makereport(item,call):
    '''
        pytest_runtest_makereport()是pytest内置的钩子名称，不能改。类似生命周期函数
        pytest_sessionstart 整个测试会话开始前
        pytest_runtest_setup 测试用例开始前（setUp）
        pytest_runtest_makereport 测试用例执行完生成报告时
        pytest_runtest_teardown 测试用例结束后（tearDown）
        pytest_sessionfinnish 整个测试会话结束后

        item:测试用例对象，包含函数名，测试参数，fixture等
        call:当前执行阶段(setup/call/teardown), 用于控制什么时候进行该操作

        report.when    # 执行阶段：'setup'/'call'/'teardown'
        report.failed  # 是否失败（True/False）
        report.passed  # 是否通过
        report.skipped # 是否跳过
        report.longreprtext  # 详细的错误信息（堆栈）
    '''
    outcome=yield
    # 该句是关键，将控制权交出来，且outcome包含测试结果
    report=outcome.get_result()

    def attach_png_reprtext_to_allure():
        driver=item.funcargs.get('driver') # 获取参数driver 但driver是fixture产生的，所以是获取fixture的driver
        if driver:
            # 自动添加失败图片
            allure.attach(
                driver.get_screenshot_as_png(), # 保存到报告中显示
                name='失败截图',
                attachment_type=allure.attachment_type.PNG
            )

            allure.attach(
                f"用例：{item.nodeid}\n错误：{report.longreprtext}",
                # item.nodeid 当前测试用例完整路径
                # report.longreprtext 测试失败时的完整错误报告
                name="错误详情",
                attachment_type=allure.attachment_type.TEXT
            )
    # 获取hook装饰测试方法的测试报告report"对象"
    if report.when=='call' and report.failed:
        # 只在测试进行中（setup 和 teardown之间）同时 要测试结果是failed时，才会执行下面的操作
        attach_png_reprtext_to_allure()

    # if report.when=='call' and report.error:      不存在error类型，failed已经包含所有错误类型，assertionerror exception errpr
    #     attach_png_reprtext_to_allure()


