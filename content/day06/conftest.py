'''
    创建钩子函数用于对测试失败的用例进行图片截图同时显示在allure报告上；此出的钩子函数是根目录级别

'''

import allure,os,glob,datetime
from pathlib import Path
import pytest
import pandas  as pd
from loguru import logger
import shutil,sys


def pytest_configure(config):
    # pytest_configure  pytest自带
    logger.remove()
    # 避免重复
    log_dir=Path(__file__).parent / 'logs'
    os.makedirs(log_dir,exist_ok=True)
    logs_numbers=len(os.listdir(log_dir))
    worker_id=os.getenv('PYTEST_XDIST_WORKER','main')
    
    if worker_id=='main':
        for i in log_dir.iterdir():
            if i.is_file():
                os.remove(log_dir / i)
    # iterdir is_file is_dir都是Path的方法
    # 方法 A：使用 Path 对象（推荐）
    dirs = [dir for dir in log_dir.iterdir() if dir.is_dir()]  # 只取目录
    # [x for x in items if x > 0] 过滤条件
    # [x if x > 0 else 0 for x in items] 条件表达式
    dirs.sort(key=lambda x: x.stat().st_mtime)  # 按修改时间升序（旧的在前）
    # sort是方法，在原有列表修改，快
    # sorted是函数，需要变量接值，慢
    if worker_id=='main':
        if logs_numbers>=10:
            for dir in dirs:
                # 默认升序
                shutil.rmtree(log_dir / dir)
                # 直接递归删除
                if len(os.listdir(log_dir))<=10:
                    break
    if worker_id=='main':
        timestamp=datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')
        os.makedirs(log_dir / f'{timestamp}_dir')
        curr_file_path=log_dir / f'{timestamp}_dir' / f'{worker_id}_{timestamp}.txt'
    else:
        # shutil.rmtree(log_dir / 'gws')
        os.makedirs(log_dir / 'gws',exist_ok=True)
        curr_file_path=log_dir / 'gws' / f'{worker_id}.txt'

    # 存进进程级全局
    logger.configure(extra={"worker_id":worker_id})
    # 多进程写进各自不同文件
    logger.add(
        curr_file_path,
        level='INFO',       # level级别必须大写
        format='{time:YYYY-MM-DD HH:mm:ss} - worker_id={extra[worker_id]} - {module} - {level} - {message}',
        enqueue=True,   # 多进程问题
        encoding='utf-8'
    )
    # 添加输出至终端
    logger.add(
        sys.stderr,       # 输出至终端，只要级别大于等于INFO
        format='{time:YYYY-MM-DD HH:mm:ss} - {extra[worker_id]} - {module} - {level} - {message}',
        level="INFO"
    )
    logger.info(f'日志配置以及完毕，开始输入{curr_file_path}, 打印至终端')




@pytest.hookimpl(tryfirst=True,hookwrapper=True)
# 参数tryfirst是多个钩子函数，该被装饰函数将第一个执行，hookwrapper这是一个钩子包装器，可以控制钩子前后的执行逻辑
# 被装饰函数，每一个测试函数|方法，会自动执行
def pytest_runtest_makereport(item,call):
    '''
        pytest_runtest_makereport(item,call)是pytest内置的钩子名称，不能改。类似生命周期函数

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
        try:
            driver=item.funcargs.get('driver') # 获取参数driver 但driver是fixture产生的，所以是获取fixture的driver
            logger.info('获取到driver实例，准备失败截图')
            if driver:
                # 设置页面加载和脚本超时（如果还没设置）
                driver.set_page_load_timeout(30)
                # 自动添加失败图片
                allure.attach(
                    driver.get_screenshot_as_png(), # 保存到报告中显示
                    name='失败截图',
                    attachment_type=allure.attachment_type.PNG
                )
                logger.warning('失败截图成功')
                allure.attach(
                    f"用例：{item.nodeid}\n错误：{report.longreprtext}",
                    # item.nodeid 当前测试用例完整路径
                    # report.longreprtext 测试失败时的完整错误报告
                    name="错误详情",
                    attachment_type=allure.attachment_type.TEXT
                )
                logger.warning('失败信息成上传')
            # 获取hook装饰测试方法的测试报告report"对象"
            if report.when=='call' and report.failed:
                # 只在测试进行中（setup 和 teardown之间）同时 要测试结果是failed时，才会执行下面的操作
                attach_png_reprtext_to_allure()

            # if report.when=='call' and report.error:      不存在error类型，failed已经包含所有错误类型，assertionerror exception errpr
            #     attach_png_reprtext_to_allure()
        except Exception as e:

            allure.attach(f"未知错误: {str(e)}", "截图失败", allure.attachment_type.TEXT)
            logger.warning('没能成功失败截图')
    
    



def pytest_sessionfinish(session,exitstatus):
    '''测试会话结束仅从自动数据合并'''
    # 不同进程，就会有不同的会话且执行不同的用例，因此需要判断，当前进程是主进程master么？如果是则下一步，不是则不会处理

    # 判断当前进程是不是主进程
    if os.getenv('PYTEST_XDIST_WORKER'):
        logger.warning('当前是多进程合并excel')
        return
        # 如果是主进程，则使用return 退出，不会进一步处理
    
    # 关键修复1：同时查找根目录和 test_cases/ 下的临时文件
    base_dir = Path(__file__).resolve().parent
    temp_files = glob.glob(str(base_dir / "test_cases" / 'temp_result_*.xlsx'))
    temp_files += glob.glob(str(base_dir / 'temp_result_*.xlsx'))  # 加上根目录查找
    # 使用glob.glob查找指定类型的文件，支持正则。返回列表，默认当前路径查找
    if not bool(temp_files):
        logger.warning('没有找到临时需要合并的excel文件')
        return
    # 不存在临时文件也会退出，不会后面的操作

    all_data=[]
    for file in temp_files:
        data_df=pd.read_excel(file,index_col=False)
        # index_col是控制那一列最为行索引号，默认是0,就是不适用数据列作为索引号，使用数字1 2 3 
        # 默认返回pd.DataFrame类型
        all_data.append(data_df)
        # 带上df便于辨别类型, 由于pd.concat第一个参数是要合并的数据，要求里面的类型均是pd.DataFrame类型;eg：[pd.DataFrame1,pd.DataFrame2]
        os.remove(file)
        # 当临时文件使用完毕进行删除，节约空间。
        logger.info('成功合并数据')
    
    final_result=pd.concat(all_data,ignore_index=True)
    # 合并数据all_data ： [pd.DataFrame1,pd.DataFrame2];axis=0 默认纵坐标拼接
    timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    # 关键修复2：确保目录存在后再生成文件路径
    report_dir = base_dir / 'report'
    report_dir.mkdir(exist_ok=True)  # 先创建目录

    final_file=str(Path(__file__).resolve().parent / 'report' / f'test_report_{timestamp}.xlsx')
    # 去重
    final_result=final_result.drop_duplicates(subset=['case_id'],keep='last')
    final_result.to_excel(final_file,index=False)
    logger.success(f"✅ 最终报告已生成: {final_file}（共 {len(final_result)} 条记录）")