from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = datetime.now()
    current_year = current_date.year
    return {
        'year': current_year
    }
