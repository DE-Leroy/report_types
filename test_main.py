import pytest
from main import LogProcessor

# Фикстура для создания временных лог-файлов
@pytest.fixture
def temp_log_files(tmp_path):
    log_content = [
        "2025-04-27 01:00:00 INFO django.request: GET /api/v1/users/ 200 OK [127.0.0.1]",
        "2025-04-27 01:01:00 ERROR django.request: POST /api/v1/users/ 500 Internal Server Error [127.0.0.1] - ValueError: Invalid data",
        "2025-04-27 01:02:00 INFO django.request: GET /api/v1/products/ 200 OK [127.0.0.1]",
        "2025-04-27 01:03:00 DEBUG django.db.backends: SELECT * FROM users;",
        "2025-04-27 01:04:00 INFO django.request: GET /api/v1/users/ 204 No Content [127.0.0.1]",
        "2025-04-27 01:05:00 WARNING django.security: SuspiciousOperation: Attempted access to '/admin/' denied.",
        "2025-04-27 01:06:00 CRITICAL django.core.management: DatabaseError: Connection refused",
        "2025-04-27 01:07:00 INFO django.request: GET /api/v1/reviews/ 200 OK [127.0.0.1]",
        "2025-04-27 01:08:00 ERROR django.request: GET /api/v1/reviews/ 404 Not Found [127.0.0.1]",
    ]
    file1 = tmp_path / "test_log1.txt"
    file1.write_text("\n".join(log_content[:5]))
    file2 = tmp_path / "test_log2.txt"
    file2.write_text("\n".join(log_content[5:]))
    return [str(file1), str(file2)]

# Тест обработки логов и подсчета handlers
def test_process_handlers_report(temp_log_files):
    processor = LogProcessor(temp_log_files, 'handlers')
    processor.process_files_parallel()
    levels_name = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']
    for handler_name in processor.output:
        for level in levels_name:
            assert level in processor.output[handler_name]
            assert type(processor.output[handler_name][level]) is int
    assert processor.output['/api/v1/users/']['INFO'] == 2
    assert processor.output['/api/v1/users/']['ERROR'] == 1
    assert processor.output['/api/v1/products/']['INFO'] == 1
    assert processor.output['/api/v1/reviews/']['INFO'] == 1 
    assert processor.output['/api/v1/reviews/']['ERROR'] == 1

# Тест обработки с одним файлом
def test_process_handlers_single_file(tmp_path):
    log_content = [
        "2025-04-27 01:00:00 INFO django.request: GET /api/v1/items/ 200 OK [127.0.0.1]",
        "2025-04-27 01:01:00 ERROR django.request: POST /api/v1/items/ 500 Internal Server Error [127.0.0.1]",
    ]
    log_file = tmp_path / "single_log.txt"
    log_file.write_text("\n".join(log_content))
    processor = LogProcessor([str(log_file)], 'handlers')
    processor.process_files_parallel()
    assert "/api/v1/items/" in processor.output
    assert processor.output["/api/v1/items/"]["INFO"] == 1
    assert processor.output["/api/v1/items/"]["ERROR"] == 1

# Тест обработки пустого лог-файла
def test_process_handlers_empty_file(tmp_path):
    log_file = tmp_path / "empty_log.txt"
    log_file.write_text("")
    processor = LogProcessor([str(log_file)], 'handlers')
    processor.process_files_parallel()
    assert not processor.output

# Тест обработки файла без логов django.request
def test_process_handlers_no_django_request(tmp_path):
    log_content = [
        "2025-04-27 01:00:00 INFO some_other_log: Something happened",
        "2025-04-27 01:01:00 ERROR another_log: An error occurred",
    ]
    log_file = tmp_path / "no_django_log.txt"
    log_file.write_text("\n".join(log_content))
    processor = LogProcessor([str(log_file)], 'handlers')
    processor.process_files_parallel()
    assert not processor.output

# Тест обработки несуществующего файла (проверяем, что не падает)
def test_process_non_existent_file():
    processor = LogProcessor(['non_existent.log'], 'handlers')
    processor.process_files_parallel()
    # Проверяем, что output остается пустым или логируется сообщение об ошибке (stdout)
    assert not processor.output

# Тест корректного вывода отчета handlers (проверяем наличие определенных строк в stdout)
def test_handlers_report_output(temp_log_files, capsys):
    processor = LogProcessor(temp_log_files, 'handlers')
    processor.process_files_parallel()
    processor._handlers_print()
    captured = capsys.readouterr()
    assert "Total requests:" in captured.out
    assert "HANDLER" in captured.out
    assert "/api/v1/users/" in captured.out
    assert "/api/v1/products/" in captured.out
    assert "INFO" in captured.out
    assert "ERROR" in captured.out
