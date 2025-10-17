"""Automation script for network configurator task search."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class TaskSearchConfig:
    base_url: str = "https://186.130.131.62:8443/login.html"
    username: str = "malagolir"
    password: str = "operweb"
    equipo_filter: str = "[OLT]"
    date_from: str = "[DESDE]"
    date_to: str = "[HASTA]"
    search_string: str = "[CADENA]"
    implicit_wait: int = 5
    explicit_wait: int = 20


class NetworkConfiguratorScraper:
    def __init__(self, driver: webdriver.Remote, config: TaskSearchConfig) -> None:
        self.driver = driver
        self.config = config
        self.driver.implicitly_wait(config.implicit_wait)

    def login(self) -> None:
        self.driver.get(self.config.base_url)
        wait = WebDriverWait(self.driver, self.config.explicit_wait)

        username_input = wait.until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        password_input = wait.until(
            EC.element_to_be_clickable((By.NAME, "password"))
        )

        username_input.clear()
        username_input.send_keys(self.config.username)
        password_input.clear()
        password_input.send_keys(self.config.password)

        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "nav")))

    def open_task_list(self) -> None:
        wait = WebDriverWait(self.driver, self.config.explicit_wait)

        otros_menu = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Otros"))
        )
        otros_menu.click()

        configurator_menu = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Configurador de Recursos de Red"))
        )
        configurator_menu.click()

        task_list_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Listado de Tareas de Configuración"))
        )
        task_list_link.click()

        wait.until(EC.presence_of_element_located((By.ID, "search-form")))

    def apply_filters(self) -> None:
        wait = WebDriverWait(self.driver, self.config.explicit_wait)

        equipo_input = wait.until(
            EC.element_to_be_clickable((By.ID, "equipo"))
        )
        equipo_input.clear()
        equipo_input.send_keys(self.config.equipo_filter)

        date_from_input = self.driver.find_element(By.ID, "fecha-desde")
        date_from_input.clear()
        date_from_input.send_keys(self.config.date_from)

        date_to_input = self.driver.find_element(By.ID, "fecha-hasta")
        date_to_input.clear()
        date_to_input.send_keys(self.config.date_to)

        search_button = self.driver.find_element(By.CSS_SELECTOR, "button.buscar")
        search_button.click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))

    def _open_history(self, row) -> str:
        history_button = row.find_element(By.CSS_SELECTOR, "button.ver-historico")
        history_button.click()

        wait = WebDriverWait(self.driver, self.config.explicit_wait)
        history_panel = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.historial"))
        )
        return history_panel.text

    def _close_history(self) -> None:
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, "div.historial button.cerrar")
            close_button.click()
        except NoSuchElementException:
            pass

    def _collect_rows(self) -> List[webdriver.remote.webelement.WebElement]:
        table = self.driver.find_element(By.CSS_SELECTOR, "table tbody")
        return table.find_elements(By.TAG_NAME, "tr")

    def _go_to_next_page(self) -> bool:
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "ul.pagination li.next:not(.disabled) a")
        except NoSuchElementException:
            return False

        next_button.click()
        wait = WebDriverWait(self.driver, self.config.explicit_wait)
        wait.until(EC.staleness_of(self.driver.find_element(By.CSS_SELECTOR, "table tbody tr")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
        return True

    def find_matching_tasks(self) -> List[str]:
        matches: List[str] = []
        while True:
            rows = self._collect_rows()
            for row in rows:
                task_id = row.find_element(By.CSS_SELECTOR, "td.id-tarea").text.strip()
                history_text = self._open_history(row)
                if self.config.search_string in history_text:
                    matches.append(task_id)
                self._close_history()

            if not self._go_to_next_page():
                break
        return matches


def main() -> None:
    config = TaskSearchConfig()
    matches: List[str] = []
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    with webdriver.Chrome(options=options) as driver:
        scraper = NetworkConfiguratorScraper(driver, config)
        try:
            scraper.login()
            scraper.open_task_list()
            scraper.apply_filters()
            matches = scraper.find_matching_tasks()
        except TimeoutException as exc:
            print(f"Timeout while interacting with the site: {exc}")
            return

    if matches:
        for task_id in matches:
            print(task_id)
    else:
        print("Sin coincidencias encontradas")


if __name__ == "__main__":
    main()
