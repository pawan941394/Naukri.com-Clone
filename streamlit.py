import streamlit as st
import pandas as pd
import requests
import urllib.parse
import re
from datetime import datetime, timedelta
from style import styles, youtube
# Import functions from your SCRAPPER.py
from NaukriWebScrapper.headers import headers_naukri
from NaukriWebScrapper.cookies import cookies_naukri

def fetch_jobs(job_title, page_number):
    """Fetch job listings from Naukri.com"""
    
    # URL encode the job title for the search query
    encoded_title = urllib.parse.quote(job_title)
    
    # Define headers and cookies
    headers = headers_naukri(encoded_title)
    cookies = cookies_naukri()
    
    # Use a session to maintain cookies
    session = requests.Session()
    
    # Construct the dynamic URL based on job title
    url = f"https://www.naukri.com/jobapi/v3/search?noOfResults=20&urlType=search_by_keyword&searchType=adv&keyword={encoded_title}&sort=r&pageNo={page_number}&k={encoded_title}&nignbevent_src=jobsearchDeskGNB&seoKey={encoded_title.lower().replace(' ', '-')}-jobs&src=jobsearchDesk&latLong="
    
    # Make the request
    response = session.get(url, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

def categorize_posting_time(posted_text):
    """
    Categorize job posting time into standard periods:
    - Today
    - Yesterday
    - This Week (2-7 days)
    - This Month (8-30 days)
    - Older (more than 30 days)
    """
    if not posted_text or posted_text == "N/A":
        return "Unknown"
    
    # Extract number of days, hours, or minutes
    days_match = re.search(r'(\d+)\s*day', posted_text.lower())
    hours_match = re.search(r'(\d+)\s*hour', posted_text.lower())
    minutes_match = re.search(r'(\d+)\s*minute', posted_text.lower())
    
    if "just now" in posted_text.lower() or "few seconds" in posted_text.lower() or minutes_match:
        return "Today"
    elif hours_match:
        return "Today"
    elif "yesterday" in posted_text.lower():
        return "Yesterday"
    elif days_match:
        days = int(days_match.group(1))
        if days < 2:
            return "Yesterday"
        elif days <= 7:
            return "This Week"
        elif days <= 30:
            return "This Month"
        else:
            return "Older"
    elif "week" in posted_text.lower():
        return "This Week"
    elif "month" in posted_text.lower():
        if "1 month" in posted_text.lower():
            return "This Month"
        else:
            return "Older"
    else:
        return "Unknown"

def main():
    # Make set_page_config the first Streamlit command
    st.set_page_config(
        page_title="Naukri.com Job Scraper",
        page_icon="🔍",
        layout="wide"
    )
    
    # Add custom CSS for better styling AFTER page config
    st.markdown(f'{styles()}', unsafe_allow_html=True)
    
    # Header with YouTube channel link
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔍 Naukri.com Job Scraper")
        st.write("Search for jobs on Naukri.com and view the results.")
    with col2:
        st.markdown("""
        <div style="text-align: right; margin-top: 20px;">
            <a href="https://www.youtube.com/@Pawankumar-py4tk" target="_blank" class="youtube-btn">
                <span class="youtube-icon">▶️</span> Subscribe on YouTube
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Create a form for user input
    with st.form(key="search_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            job_title = st.text_input("Enter job title to search", placeholder="e.g. Python Developer")
        with col2:
            page_number = st.text_input("Page number", value="1")
        
        submit_button = st.form_submit_button(label="Search Jobs")
    
    # Store the data in session state to prevent it from disappearing when filter is applied
    if submit_button and job_title:
        with st.spinner(f"Searching for '{job_title}' jobs on Naukri.com..."):
            data = fetch_jobs(job_title, page_number)
            if data and "jobDetails" in data:
                st.session_state['job_data'] = data
                st.session_state['job_title'] = job_title
                st.session_state['page_number'] = page_number
                # Clear any existing filter selection
                if 'posting_filter' in st.session_state:
                    del st.session_state['posting_filter']
    
    # Process and display data if available in session state
    if 'job_data' in st.session_state:
        data = st.session_state['job_data']
        job_title = st.session_state['job_title']
        
        if "jobDetails" in data:
            job_count = len(data['jobDetails'])
            st.success(f"Found {job_count} job listings for '{job_title}'")
            
            # Add job IDs to make matching easier later
            for i, job in enumerate(data["jobDetails"]):
                job['index'] = i
            
            # Convert job details to a list of dictionaries for pandas
            jobs_list = []
            
            for i, job in enumerate(data["jobDetails"]):
                # Process location and salary
                location = "N/A"
                salary = "N/A"
                if "placeholders" in job and isinstance(job["placeholders"], list):
                    for placeholder in job["placeholders"]:
                        if placeholder.get("type") == "location":
                            location = placeholder.get("label", "N/A")
                        if placeholder.get("type") == "salary":
                            salary = placeholder.get("label", "N/A")
                
                posted_time = job.get("footerPlaceholderLabel", "N/A")
                posting_category = categorize_posting_time(posted_time)
                
                jobs_list.append({
                    "Title": job.get("title", "N/A"),
                    "Company": job.get("companyName", "N/A"),
                    "Experience": job.get("experienceText", "N/A"),
                    "Location": location,
                    "Salary": salary,
                    "Posted": posted_time,
                    "PostingCategory": posting_category,
                    "Skills": job.get("tagsAndSkills", "N/A"),
                    "Job URL": f"https://www.naukri.com{job.get('jdURL', 'N/A')}",
                    "JobId": job.get("jobId", "N/A"),
                    "Index": i  # Use the loop index directly
                })
            
            # Create a DataFrame
            df = pd.DataFrame(jobs_list)
            
            # Store DataFrame in session state
            st.session_state['jobs_df'] = df
            
            # Add filter for posting times
            st.write("### Filter Jobs")
            
            # Get unique posting categories and ensure they're in a logical order
            categories = df['PostingCategory'].unique().tolist()
            ordered_categories = []
            for cat in ["Today", "Yesterday", "This Week", "This Month", "Older", "Unknown"]:
                if cat in categories:
                    ordered_categories.append(cat)
            
            # Add an "All" option at the beginning
            filter_options = ["All"] + ordered_categories
            
            # Create filter outside of columns to ensure it's always visible
            posting_filter = st.selectbox(
                "Filter by posting time:", 
                filter_options,
                key="posting_time_filter",
                index=0  # Default to "All"
            )
            
            # Filter the DataFrame based on selection
            if posting_filter != "All":
                filtered_df = df[df['PostingCategory'] == posting_filter]
                st.write(f"Showing {len(filtered_df)} jobs posted {posting_filter.lower()}")
            else:
                filtered_df = df
                st.write(f"Showing all {len(filtered_df)} jobs")
            
            # Add debugging information
            st.write(f"Original data had {len(df)} jobs, filtered data has {len(filtered_df)} jobs")
            
            # Display message if no jobs match filter
            if len(filtered_df) == 0:
                st.warning(f"No jobs found with posting time: {posting_filter}")
            else:
                # Add a download button for filtered results
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download filtered results as CSV",
                    data=csv,
                    file_name=f"naukri_{job_title.lower().replace(' ', '_')}_{posting_filter.lower().replace(' ', '_')}_jobs.csv",
                    mime="text/csv",
                )
                
                # Display the filtered results
                for i, (_, job_row) in enumerate(filtered_df.iterrows()):
                    # Use the stored index to get the original job data
                    job_index = int(job_row['Index'])
                    
                    if 0 <= job_index < len(data["jobDetails"]):
                        job = data["jobDetails"][job_index]
                        job_title_text = job.get('title', 'N/A')
                        company_name = job.get('companyName', 'N/A')
                        
                        # Rest of job display code
                        with st.expander(f"{i+1}. {job_title_text} at {company_name} ({job_row['PostingCategory']})"):
                            # Get company logo
                            logo_url = job.get('companyLogoUrl', None)
                            
                            # Get location and salary
                            location = job_row['Location']
                            salary = job_row['Salary']
                            
                            # Create a card-like layout for the job
                            st.markdown('<div class="job-card">', unsafe_allow_html=True)
                            
                            # Job header with logo and title
                            logo_col, title_col = st.columns([1, 4])
                            
                            with logo_col:
                                if logo_url:
                                    st.markdown(f'<img src="{logo_url}" class="company-logo" alt="{company_name} logo">', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div style="height:50px; display:flex; align-items:center; justify-content:center; background-color:#eee; border-radius:5px;">{company_name[0]}</div>', unsafe_allow_html=True)
                            
                            with title_col:
                                st.markdown(f"<h3>{job_title_text}</h3>", unsafe_allow_html=True)
                                st.markdown(f"<h4>{company_name}</h4>", unsafe_allow_html=True)
                            
                            # Job details in 3 columns
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.write(f"**Experience:** {job.get('experienceText', 'N/A')}")
                                st.write(f"**Location:** {location}")
                                st.write(f"**Posted:** {job.get('footerPlaceholderLabel', 'N/A')} ({job_row['PostingCategory']})")
                            
                            with col2:
                                st.write(f"**Salary:** {salary}")
                                st.write(f"**Skills:** {job.get('tagsAndSkills', 'N/A')}")
                            
                            with col3:
                                job_url = f"https://www.naukri.com{job.get('jdURL', 'N/A')}"
                                st.markdown(f'<a href="{job_url}" target="_blank" class="apply-button">Apply Now</a>', unsafe_allow_html=True)
                            
                            # Job description
                            st.write("**Job Description:**")
                            job_desc = job.get("jobDescription", "N/A")
                            
                            # Use HTML rendering for the job description
                            if job_desc != "N/A":
                                st.markdown(f'<div class="job-description">{job_desc}</div>', unsafe_allow_html=True)
                            else:
                                st.write("No job description available.")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"Could not find job details for {job_row['Title']} at {job_row['Company']} (Index: {job_index})")
        else:
            st.error("No job details found in the data.")
    
    # Display search message if no data is loaded yet
    elif not submit_button:
        st.info("Enter a job title and click 'Search Jobs' to start.")
    
    # Display footer with YouTube channel at the end of the page
    st.markdown(f'{youtube()}', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
