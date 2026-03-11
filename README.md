# Adaptive Quiz System (AQDS)

A dynamic quiz application that adapts to student performance levels, providing personalized learning experiences with detailed performance analytics.

## Features

- 🎯 **Adaptive Difficulty** - Questions adjust based on student performance
- 📊 **Real-time Analytics** - Track progress with interactive charts
- 📈 **Performance Reports** - Download detailed PDF reports
- 🎨 **Modern UI** - Clean, responsive interface with gradient designs
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

## Performance Report

The system generates comprehensive performance reports including:
- Total Questions Attempted
- Correct Answers
- Accuracy Percentage
- Current Difficulty Level
- Difficulty Distribution Chart
- Score Progress Over Time Chart

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**
   ```bash
   cd D:\Work\AQDS
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## Project Structure

```
AQDS/
├── app.py                 # Main Flask application
├── models.py              # Data models and business logic
├── import_questions.py    # Question import utility
├── insert_questions.sql   # SQL script for database setup
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── data/
│   ├── questions.json     # Question bank
│   ├── learners.json      # Student data
│   ├── logs.json          # Activity logs
│   └── analytics.json     # Analytics data
├── templates/
│   ├── index.html         # Home page
│   ├── quiz.html          # Quiz interface
│   └── dashboard.html     # Performance dashboard
├── static/
│   └── style.css          # Stylesheets
└── README.md              # This file
```

## Usage

### Starting a Quiz
1. Enter your username on the home page
2. Click "Start Quiz"
3. Answer questions adaptively based on your performance

### Viewing Results
1. Complete the quiz session
2. Automatically redirected to dashboard
3. View performance metrics and charts

### Downloading PDF Report
1. On the dashboard, click "📥 Download PDF Report"
2. PDF will download with complete performance analytics
3. Report includes all metrics and charts as shown on screen

## Configuration

### Environment Variables (.env)
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

### Data Files
- **questions.json**: Store quiz questions with difficulty levels
- **learners.json**: Student profiles and progress tracking
- **logs.json**: Activity and attempt history

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **PDF Generation**: html2canvas + jsPDF
- **Fonts**: Google Fonts (Inter)

## Browser Compatibility

For best PDF export results, use:
- Google Chrome (recommended)
- Microsoft Edge
- Mozilla Firefox

## Troubleshooting

### PDF Download Issues
- Ensure pop-ups are not blocked in your browser
- Wait for charts to fully load before downloading
- Use Chrome browser for best compatibility

### Application Not Starting
- Check if all dependencies are installed: `pip install -r requirements.txt`
- Ensure port 5000 is not in use
- Verify Python version is 3.8 or higher

## License

This project is for educational purposes.

## Support

For issues or questions, please check the code documentation or contact the development team.
