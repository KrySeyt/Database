import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ..storage import schema as storage_schema
from ..statistics import service as statistics_service


async def get_title_employees_growth(
        db: AsyncSession,
        title: storage_schema.TitleIn,
        years_count: int
) -> dict[int, int]:

    assert years_count > 0

    employees_growth_forecast: dict[int, int] = {}
    employees_growth_history: dict[int, int] = await statistics_service.get_title_employees_growth_history(db, title)
    if not employees_growth_history:
        return {}

    for _ in range(years_count):
        employees_growth_info = {
            **employees_growth_history,
            **employees_growth_forecast
        }

        if len(employees_growth_info) < 5:
            next_year_growth_neighbours_count = len(employees_growth_info)
        else:
            next_year_growth_neighbours_count = 5

        growth_info_years = list(employees_growth_info.keys())
        growth_info_years.sort(reverse=True)
        neighbour_years = growth_info_years[:next_year_growth_neighbours_count]

        next_years_growth = 0
        for year in neighbour_years:
            next_years_growth += employees_growth_info[year]

        next_years_growth = round(next_years_growth / next_year_growth_neighbours_count)

        current_max_year = max(growth_info_years)
        employees_growth_forecast[current_max_year + 1] = next_years_growth

    return employees_growth_forecast
