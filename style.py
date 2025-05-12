def styles():
    return """

<style>
    .job-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .job-description {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
        line-height: 1.5;
    }
    .job-description p {
        margin-bottom: 10px;
    }
    .company-logo {
        max-width: 100px;
        max-height: 50px;
        margin-bottom: 10px;
    }
    .job-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .apply-button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        border-radius: 4px;
    }
    .footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        text-align: center;
    }
    .youtube-btn {
        display: inline-flex;
        align-items: center;
        background-color: #FF0000;
        color: white !important;
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 4px;
        margin: 10px 0;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .youtube-btn:hover {
        background-color: #cc0000;
    }
    .youtube-icon {
        margin-right: 8px;
        font-size: 20px;
    }
    </style>
"""


def youtube():
    return """
 <div class="footer">
        <p>Developed by <a href="https://www.youtube.com/@Pawankumar-py4tk" target="_blank">Pawan Kumar</a></p>
        <a href="https://www.youtube.com/@Pawankumar-py4tk" target="_blank" class="youtube-btn">
            <span class="youtube-icon">▶️</span> Subscribe to my YouTube Channel for more Python tutorials
        </a>
        <p style="font-size: 0.8em; margin-top: 10px;">© 2023 All Rights Reserved</p>
    </div>
    """