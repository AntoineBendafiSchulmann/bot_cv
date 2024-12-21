import json
from playwright.sync_api import sync_playwright


def load_sectors(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def choose_sector(sectors):
    print("Choisissez un secteur parmi les suivants :")
    for i, sector in enumerate(sectors.keys(), start=1):
        print(f"{i}. {sector}")
    choice = int(input("Entrez le numéro du secteur : ")) - 1
    return list(sectors.values())[choice], list(sectors.keys())[choice]

def scrape_company_urls_and_jobs(sector_filter, sector_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        base_url = f"https://www.welcometothejungle.com/fr/companies?page={{page}}&query=&{sector_filter}"
        page_number = 1
        developer_keywords = ["developpeur", "developer", "software", "frontend", "backend", "fullstack", "engineer"]

        print(f"\n[INFO] Scraping des entreprises pour le secteur : {sector_name}\n")
        while True:
            url = base_url.format(page=page_number)
            print(f"Chargement des offres pour la page {page_number} ...")
            page.goto(url)

            for _ in range(10):
                page.mouse.wheel(0, 1000)
                page.wait_for_timeout(500)

            links = page.locator('a[href*="/fr/companies/"]').all()

            companies_with_jobs = set()
            for link in links:
                href = link.get_attribute("href")
                if href and "/jobs" in href:
                    company_name = href.split("/fr/companies/")[-1].split("/jobs")[0]
                    companies_with_jobs.add(f"https://www.welcometothejungle.com/fr/companies/{company_name}/jobs")

            if not companies_with_jobs:
                print("\n[INFO] Fin de la pagination. Toutes les pages disponibles ont été parcourues.\n")
                break

            for jobs_url in sorted(companies_with_jobs):
                company_name = jobs_url.split("/fr/companies/")[-1].split("/jobs")[0]
                page.goto(jobs_url)
                page.wait_for_timeout(3000)

                job_links = page.locator('a[href*="/jobs/"]').all()

                developer_jobs = []
                for job_link in job_links:
                    job_url = job_link.get_attribute("href")
                    if job_url and any(keyword in job_url.lower() for keyword in developer_keywords):
                        developer_jobs.append(job_url)

                if developer_jobs:
                    print(f"\nEntreprise : {company_name}")
                    print(f"Vérification des offres sur : {jobs_url}")
                    print(f" - {len(developer_jobs)} offres pour développeurs trouvées :")
                    for job in developer_jobs:
                        print(f"   * {job}")

            page_number += 1

        browser.close()

sectors = load_sectors("sectors.json")
sector_filter, sector_name = choose_sector(sectors)
scrape_company_urls_and_jobs(sector_filter, sector_name)
