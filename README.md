# Практическая работа №1. Вариант 30

Этап 1: графический прототип UNIX-оболочки на Python и Tkinter.
Заголовок содержит реальные username и hostname. Парсер разделяет
ввод по пробелам; ls и cd пока выводят имя и аргументы. Команда exit
закрывает окно. Неизвестные команды выводят сообщение об ошибке.

## Запуск

Требуется Python 3.10+ с Tkinter. Windows: `run.bat`.
Linux/macOS: `sh run.sh`. Сборка и сторонние пакеты не требуются.

## Тесты

Windows PowerShell:

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

Linux/macOS:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Интерактивная демонстрация

```text
ls /tmp
cd /home
unknown
exit extra
exit
```

Ошибки unknown и exit extra не закрывают окно.

## Этап 2. Конфигурация

`--vfs PATH` задает источник VFS (подключение в этапе 3).
`--startup PATH` задает UTF-8 сценарий. Пустые строки и строки с #
пропускаются. При первой ошибке или exit выполнение останавливается.
В окне показываются ввод и вывод каждой команды. После ошибки окно
остается открытым. `conf-dump` выводит все настройки как ключ=значение.
Настройки также показываются при запуске.

`--headless` - дополнительный режим запуска сценария без окна для тестов.
Требует `--startup`; код завершения: 0 при успехе, 1 при ошибке сценария,
2 при ошибке аргументов. Скрипты ОС: examples/demo-config.bat и .sh.

```bat
run.bat --vfs examples\vfs\deep --startup examples\scripts\stage2.txt
```
