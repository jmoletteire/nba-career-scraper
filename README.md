# NBA Career Opportunities Scraper

An automated tool that monitors all NBA team career pages for job opportunities matching your specified keywords and sends email notifications with the results.

## 🏀 Features

- **Automated Discovery**: Discovers all NBA team career page URLs from the main NBA careers site
- **Smart Scraping**: Handles different website structures and pagination across team sites
- **Keyword Filtering**: Filters jobs based on customizable keywords/phrases
- **Email Notifications**: Sends formatted email reports with job details and application links
- **Duplicate Detection**: Avoids sending duplicate job notifications
- **Logging**: Comprehensive logging for monitoring and debugging
- **Periodic Execution**: Can run as a one-time check or on a schedule

## 📁 Project Structure

```
nba-career-scraper/
├── src/
│   ├── main.py            # Entry point and orchestration
│   ├── scraper.py         # Core scraping logic for NBA career pages
│   ├── email_sender.py    # Email composition and sending
│   ├── config.py          # Configuration management
│   └── utils.py           # Utility functions and helpers
├── data/
│   ├── team_urls.json     # Auto-discovered NBA team career URLs
│   └── keywords.json      # Job keywords to search for
├── logs/                  # Application logs
├── tests/                 # Unit tests
├── .env.example          # Environment configuration template
├── requirements.txt      # Python dependencies
├── run.sh               # Convenient run script
└── README.md
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd nba-career-scraper

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your email credentials
# For Gmail, use an App Password: https://support.google.com/accounts/answer/185833
```

Example `.env` configuration:

```env
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=recipient@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Customize Keywords

Edit `data/keywords.json` to specify the job types you're interested in:

```json
{
  "keywords": [
    "analytics",
    "data science",
    "marketing",
    "coaching",
    "scouting",
    "operations",
    "management",
    "player development",
    "sports performance",
    "communications"
  ]
}
```

### 4. Run the Scraper

```bash
# One-time check
./run.sh

# Or run directly with Python
python src/main.py

# Periodic checking (every 24 hours)
./run.sh --periodic 24

# Or with custom interval (every 12 hours)
./run.sh --periodic 12
```

## 🔧 How It Works

1. **Team Discovery**: The scraper visits https://careers.nba.com/teams/ to discover all NBA team career page URLs
2. **Content Scraping**: For each team, it navigates to their career page and extracts job listings
3. **Smart Parsing**: Uses multiple strategies to handle different website structures and find job information
4. **Keyword Matching**: Filters jobs based on title and description keyword matches
5. **Email Reports**: Formats and sends email notifications with matched jobs
6. **Logging**: Records all activities for monitoring and troubleshooting

## 📧 Email Format

The scraper sends well-formatted email reports including:

- Total number of jobs found
- Jobs grouped by team
- For each job:
  - Job title
  - Location (if available)
  - Description preview
  - Direct application link
  - Timestamp when scraped

## ⚙️ Configuration Options

### Environment Variables

| Variable               | Description                 | Default        |
| ---------------------- | --------------------------- | -------------- |
| `EMAIL_SENDER`         | Your email address          | Required       |
| `EMAIL_PASSWORD`       | Email password/app password | Required       |
| `EMAIL_RECIPIENT`      | Recipient email address     | Same as sender |
| `SMTP_SERVER`          | SMTP server address         | smtp.gmail.com |
| `SMTP_PORT`            | SMTP server port            | 587            |
| `CHECK_INTERVAL_HOURS` | Hours between checks        | 24             |
| `MAX_RETRIES`          | Max retry attempts          | 3              |
| `REQUEST_TIMEOUT`      | Request timeout in seconds  | 10             |

### Data Files

- **`data/keywords.json`**: Customize job search keywords
- **`data/team_urls.json`**: Auto-generated team URLs (can be manually edited)

## 🔍 Monitoring

Logs are automatically created in the `logs/` directory with detailed information about:

- Scraping progress and results
- Email sending status
- Errors and warnings
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

1. **Email Authentication Errors**

   - Use App Passwords for Gmail instead of regular passwords
   - Enable 2-factor authentication first
   - Check SMTP settings for other email providers

2. **No Jobs Found**

   - Verify team URLs are still valid
   - Check if keywords match available jobs
   - Review logs for scraping errors

3. **Website Structure Changes**
   - NBA team sites may update their layouts
   - Check logs for parsing errors
   - The scraper uses multiple fallback strategies

### Manual Team URL Updates

If automatic discovery fails, you can manually update `data/team_urls.json`:

```json
{
  "Los Angeles Lakers": "https://www.nba.com/lakers/careers",
  "Golden State Warriors": "https://www.nba.com/warriors/careers"
}
```

## 🔄 Scheduling

### Using Cron (Linux/macOS)

```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/nba-career-scraper && ./run.sh

# Run twice daily at 9 AM and 6 PM
0 9,18 * * * cd /path/to/nba-career-scraper && ./run.sh
```

### Using Task Scheduler (Windows)

Create a scheduled task that runs:

```
Program: python
Arguments: src/main.py
Start in: C:\path\to\nba-career-scraper
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_scraper.py
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Important Notes

- **Rate Limiting**: The scraper includes delays between requests to be respectful to NBA team websites
- **Terms of Service**: Ensure your usage complies with each team's website terms of service
- **Data Accuracy**: Job listings are scraped from public pages; always verify information on the official site
- **Privacy**: Store email credentials securely and never commit them to version control

## 📄 License

This project is for educational and personal use. Please respect website terms of service and use responsibly.

---

**Happy job hunting! 🏀💼**
│ ├── test_scraper.py # Unit tests for the JobScraper class
│ └── test_email_sender.py # Unit tests for the EmailSender class
├── requirements.txt # Project dependencies
├── .env.example # Template for environment variables
├── .gitignore # Files and directories to ignore by Git
└── README.md # Project documentation

```

## Setup Instructions

1. **Clone the repository:**
```

git clone <repository-url>
cd nba-career-scraper

```

2. **Install dependencies:**
Make sure you have Python installed, then run:
```

pip install -r requirements.txt

```

3. **Configure environment variables:**
Copy `.env.example` to `.env` and fill in your email credentials and any other necessary configurations.

4. **Run the application:**
Execute the main script to start the job checking process:
```

python src/main.py

```

## Usage

The script will automatically check the specified NBA team career links at regular intervals. If it finds job listings that match the specified keywords, it will send an email with the details.

## Contribution Guidelines

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Make sure to include tests for any new features or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
```
