import argparse
from report_types import LogProcessorMethods
from typing import List, Dict

class LogProcessor(LogProcessorMethods):
    def __init__(self, log_files:List[str], report_type:str):
        self.log_files: List[str] = log_files
        self.report_type: str = report_type
        self.output: Dict[str, Dict[str, int]] = {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обрабатывает файлы логов и генерирует отчет.")
    parser.add_argument("log_files", nargs='+', help="Пути к файлам логов для обработки.")
    parser.add_argument("--report", dest="report_type", required=True, help="Тип отчета для генерации")

    args = parser.parse_args()

    processor = LogProcessor(args.log_files, args.report_type)
    processor.process_files_parallel()
