# log_processing_methods.py
import threading
from typing import List, Dict

class LogProcessorMethods:
    log_file: List[str]
    report_type: str
    output: Dict[str, Dict[str, Dict[str, int]]]
    def read_log_file(self, log_file: str, report_type: str) -> None:
        """Читает содержимое одного файла логов."""
        try:
            if report_type == 'handlers':
                self._handlers_count(log_file)
            # elif report_type == <name of new report type>:
            else:
                print(f"Введенно не верное имя отчета {report_type}")
        except FileNotFoundError:
            print(f"Поток {threading.current_thread().name}: Ошибка: Файл не найден: {log_file}")

    def process_files_parallel(self) -> None:
        """Параллельно обрабатывает все файлы журналов."""
        threads: List[threading.Thread] = []
        for log_file in self.log_files:
            thread = threading.Thread(target=self.read_log_file, args=(log_file, self.report_type))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if self.report_type == 'handlers':
            self._handlers_print()
        # elif self.report_type == <name of new report type>:

    def _handlers_print(self) -> None:
        total_requests: int = sum(sum(levels.values()) for levels in self.output.values())

        print(f"Total requests: {total_requests}\n")
        print(f"{'HANDLER':<30}\t{'DEBUG':<8}\t{'INFO':<8}\t{'WARNING':<8}\t{'ERROR':<8}\t{'CRITICAL':<8}")

        grand_total: Dict[str, int] = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
        sorted_handlers_list: List[str] = sorted(self.output.keys())
        for handler in sorted_handlers_list:
            print(f"{handler:<30}\t{self.output[handler].get('DEBUG', 0):<8}\t{self.output[handler].get('INFO', 0):<8}\t{self.output[handler].get('WARNING', 0):<8}\t{self.output[handler].get('ERROR', 0):<8}\t{self.output[handler].get('CRITICAL', 0):<8}")
            for level, count in self.output[handler].items():
                grand_total[level] += count

        print(f"{'':<30}\t{grand_total.get('DEBUG', 0):<8}\t{grand_total.get('INFO', 0):<8}\t{grand_total.get('WARNING', 0):<8}\t{grand_total.get('ERROR', 0):<8}\t{grand_total.get('CRITICAL', 0):<8}")

    def _handlers_count(self, log_file:str) -> None:
        column_names: List[str] = ['debug','info','warning','error','critical']
        temp_dict:Dict[str, Dict[str, int]] = {}
        with open(log_file) as f:
            while True:
                row: str = f.readline()
                splitting_row: List[str] = row.split()
                if 'django.request:' in splitting_row:
                    handler_name: str = next(i for i in splitting_row if i.startswith('/'))
                    if temp_dict.get(handler_name):
                            temp_dict[handler_name][splitting_row[2]] += 1
                    else:
                            temp_dict[handler_name] = {i.upper(): 0 for i in column_names}
                            temp_dict[handler_name][splitting_row[2]] += 1
                if row == '': break
            with threading.Lock():
                for key in temp_dict:
                    if self.output.get(key, 0) == 0:
                        self.output[key] = temp_dict[key]
                    else:
                        for j in self.output[key]:
                            self.output[key][j] += temp_dict[key][j]