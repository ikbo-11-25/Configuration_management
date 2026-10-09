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
