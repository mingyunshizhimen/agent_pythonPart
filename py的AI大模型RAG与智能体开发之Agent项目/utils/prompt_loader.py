from utils.config_handler import prompt_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def load_system_prompts():
    try:
        system_prompt_path=get_abs_path(prompt_config["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yml配置项中没用main_prompt_path配置项")
        raise e

    try:
        return open(system_prompt_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts]解析系统提示词出错,{str(e)}")
        raise e

def load_rag_prompts():
    try:
        rag_prompt_path=get_abs_path(prompt_config["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompts]在yml配置项中没用rag_summarize_prompt_path配置项")
        raise e

    try:
        return open(rag_prompt_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompts]解析RAG总结提示词出错,{str(e)}")
        raise e

def load_report_prompts():
    try:
        report_prompt_path=get_abs_path(prompt_config["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompts]在yml配置项中没用report_prompt_path配置项")
        raise e

    try:
        return open(report_prompt_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompts]解析报告生成提示词出错,{str(e)}")
        raise e
def load_sky_prompt():
    try:
        sky_prompt_path=get_abs_path(prompt_config["sky_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_sky_prompt]在yml配置项中没用sky_prompt_path配置项")
        raise e
    try:
        return open(sky_prompt_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_sky_prompt]解析Sky提示词出错,{str(e)}")
        raise e
if __name__=="__main__":
    print(load_system_prompts())
    print(load_rag_prompts())
    print(load_report_prompts())