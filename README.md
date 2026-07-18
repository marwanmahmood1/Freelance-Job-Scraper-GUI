# 🕵️‍♂️ Freelance Job Scraper (GUI)

A multi-threaded Python desktop application designed to automate the extraction and batch processing of job market data across any industry. 

### ⚙️ Core Features
*   **Dynamic Batch Processing:** Users can input multiple target roles across different fields (e.g., "Software Engineer, Data Analyst, Mechanical Design") for sequential data extraction.
*   **Universal Webdriver:** Implements an automated fallback sequence (Chrome -> Edge -> Firefox) to ensure successful scraping regardless of the user's local browser environment.
*   **Asynchronous UI:** Utilizes `CustomTkinter` and `threading` to maintain a highly responsive, modern interface while heavy network requests run in the background.
*   **System Tray Integration:** Runs seamlessly in the background with `pystray`, allowing users to minimize the terminal during long data extraction cycles.
*   **Multilingual Support:** Fully localized interface supporting English, Arabic, and Spanish.

### 💻 Tech Stack
*   **Frontend UI:** CustomTkinter, PIL (Image processing)
*   **Data Pipeline:** Selenium Webdriver, BeautifulSoup4
*   **Data Structuring:** Pandas (Automated CSV report generation)
