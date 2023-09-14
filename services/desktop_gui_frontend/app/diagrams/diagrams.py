import datetime
from collections import Counter

from dateutil import relativedelta
from matplotlib.figure import Figure  # type: ignore
from matplotlib import pyplot as plt  # type: ignore

from ..service.storage import schema


class DiagramsFactory:
    def create_max_employees_work_duration_diagram(self, max_work_duration_employees: list[schema.Employee]) -> Figure:
        employees_count = len(max_work_duration_employees)

        today = datetime.date.today()
        employees_names = []
        work_durations_in_month = []
        for emp in max_work_duration_employees:
            work_timedelta = relativedelta.relativedelta(today, emp.employment_date)
            work_months = (work_timedelta.years * 12) + work_timedelta.months
            work_durations_in_month.append(work_months)

            emp_name = f"{emp.name}\n{emp.surname}\n{emp.patronymic}\n({emp.id})"
            employees_names.append(emp_name)

        max_work_duration = max(work_durations_in_month) if work_durations_in_month else 0
        figure, ax = plt.subplots(figsize=(3 * employees_count, (0.2 * max_work_duration) + 2),
                                  layout='constrained')
        ax.bar(employees_names, work_durations_in_month)

        for i, duration in enumerate(work_durations_in_month):
            ax.annotate(duration, xy=(i, duration))

        return figure

    def create_highest_paid_employees_diagram(self, highest_paid_employees: list[schema.Employee]) -> Figure:
        employees_names = []
        employees_salaries_sizes_places: list[int] = []
        for i in range(len(highest_paid_employees)):
            if not employees_salaries_sizes_places:
                employees_salaries_sizes_places.append(1)
            elif highest_paid_employees[i].salary.amount == highest_paid_employees[i - 1].salary.amount and \
                    highest_paid_employees[i].salary.currency.name == highest_paid_employees[
                i - 1].salary.currency.name:
                employees_salaries_sizes_places.append(employees_salaries_sizes_places[-1])
            else:
                employees_salaries_sizes_places.append(employees_salaries_sizes_places[-1] + 1)

        employees_salaries_reprs = []
        for emp in highest_paid_employees:
            emp_salary_repr = f"{emp.salary.amount} {emp.salary.currency.name}"
            employees_salaries_reprs.append(emp_salary_repr)

            emp_name = f"{emp.name}\n{emp.surname}\n{emp.patronymic}\n({emp.id})"
            employees_names.append(emp_name)

        employees_count = len(highest_paid_employees)
        figure, ax = plt.subplots(
            figsize=(3 * employees_count, len(employees_salaries_sizes_places) + 2),
            layout='constrained'
        )

        graphs_sizes = [max(employees_salaries_sizes_places) - i + 1 for i in employees_salaries_sizes_places]
        ax.bar(employees_names, graphs_sizes)

        plt.yticks([])

        for i, salary_place in enumerate(employees_salaries_sizes_places):
            ax.annotate(employees_salaries_reprs[i], xy=(i, graphs_sizes[i]))

        return figure

    def create_title_employees_growth_diagram(self, growth_info: dict[int, int]) -> Figure:
        """

        :param growth_info: key - year; value - new employees count
        :return:
        """

        years = []
        employees_growth_per_year = []
        for year in growth_info:
            years.append(year)
            employees_growth_per_year.append(growth_info[year])

        max_employees_growth = max(employees_growth_per_year) if employees_growth_per_year else 0
        figure, ax = plt.subplots(figsize=(20, max_employees_growth + 2), layout='constrained')

        ax.bar(years, employees_growth_per_year)
        plt.xticks(years)
        plt.yticks(employees_growth_per_year)

        for i, year in enumerate(years):
            ax.annotate(employees_growth_per_year[i], xy=(year, employees_growth_per_year[i]))

        return figure

    def create_employees_distribution_by_titles_diagram(self, employees: list[schema.Employee]) -> Figure:
        emps_count_per_title: Counter[str] = Counter()
        for emp in employees:
            for title in emp.titles:
                emps_count_per_title[title.name] += 1

        figure, ax = plt.subplots(figsize=(
            20,
            10
        ), layout='constrained')

        titles: list[str] = []
        emps_counts: list[int] = []
        for title_name in emps_count_per_title:
            titles.append(title_name)
            emps_counts.append(emps_count_per_title[title_name])

        ax.bar(titles, emps_counts)
        plt.xticks(titles)
        plt.yticks(emps_counts)

        for i, emps_count in enumerate(emps_counts):
            ax.annotate(emps_count, xy=(i, emps_count))

        return figure

    def create_employees_distribution_by_topics_diagram(self, employees: list[schema.Employee]) -> Figure:
        emps_count_per_topic: Counter[str] = Counter()
        for emp in employees:
            emps_count_per_topic[emp.topic.name] += 1

        figure, ax = plt.subplots(figsize=(
            20,
            10
        ), layout='constrained')

        topics: list[str] = []
        emps_counts: list[int] = []
        for topic in emps_count_per_topic:
            topics.append(topic)
            emps_counts.append(emps_count_per_topic[topic])

        ax.bar(topics, emps_counts)
        plt.xticks(topics)
        plt.yticks(emps_counts)

        for i, emps_count in enumerate(emps_counts):
            ax.annotate(emps_count, xy=(i, emps_count))

        return figure
