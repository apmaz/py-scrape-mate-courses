from dataclasses import dataclass, fields
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
import requests


BASE_URL = "https://mate.academy/"


@dataclass
class Course:
    name: str
    short_description: str
    duration: str


COURSE_FIELDS = [field.name for field in fields(Course)]


def get_course_page_url(course_soup: Tag) -> str | None:
    url = str(course_soup.get("href"))
    if url.startswith("/courses/"):
        return urljoin(BASE_URL, url)
    print(f"URL: {url} have not /courses/")
    return None


def parce_single_course(course_url: str) -> Course:
    text = requests.get(course_url).content
    course_page_soup = BeautifulSoup(text, "html.parser")

    return Course(
        name=course_page_soup.select_one(
            ".typography_headlineLarge__qDRtr"
            ".typography_medium_headlineSmall__TUw6L"
            ".typography_small_headlineXSmall___65od"
            ".c-text-dark"
        ).text.split(":")[0].replace("\u200d", "").replace("Курс", "").strip(),

        short_description=course_page_soup.select_one(
            ".SalarySection_aboutProfessionBlock__0OV7j "
            ".SalarySection_aboutProfession__C6ftM"
        ).text.replace("\n", ""),

        duration=course_page_soup.find(
            "div",
            class_="TableColumnsView_rowTitleCell__KZkZ8",
            string="Тривалість"
        ).parent.select(
            ".TableColumnsView_tableCellGray__4hadg"
        )[1].get_text(strip=True)
    )


def get_all_courses() -> list[Course]:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    courses = soup.select(".CoursesMenuCourseList_link__47DRH")

    courses_url = [get_course_page_url(course) for course in courses]

    return [
        parce_single_course(course_url)
        for course_url in courses_url if course_url is not None
    ]


if __name__ == "__main__":
    print(get_all_courses())
