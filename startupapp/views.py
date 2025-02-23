import openpyxl
import json
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileUploadForm
from .models import Startup, UploadedFile
from datetime import datetime

logger = logging.getLogger(__name__)

import re
from datetime import datetime

def parse_date(value):
    """Convert Excel dates or string dates into Python date objects."""
    if isinstance(value, datetime):  # ✅ Already a date
        return value.date()

    if isinstance(value, str):  # ✅ Handle string formats
        value = value.strip()

        # ✅ Handle "May '23" format (Month 'YY)
        match = re.match(r"([a-zA-Z]+)\s*'(\d{2})", value)
        if match:
            month_name, year_short = match.groups()
            try:
                month = datetime.strptime(month_name, "%b").month  # Convert Month name to number
                year = int("20" + year_short)  # Convert '23 to 2023
                return datetime(year, month, 1).date()  # Default to 1st of the month
            except ValueError:
                return None  # Invalid format

        # ✅ Handle other date formats
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue  

    return None  # If conversion fails

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            success = process_excel_file(uploaded_file.file.path)

            if success:
                uploaded_file.processed = True
                uploaded_file.save()
                messages.success(request, "File uploaded and processed successfully! ✅")
            else:
                messages.error(request, "File processing failed. Please check the format.")

            return redirect('file_upload_success')
    else:
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form})

def detect_header_row(sheet, required_columns, threshold=0.4):
    """Dynamically detect the header row based on required column names."""
    for i, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        row_values = [str(cell).strip() if cell else "" for cell in row]
        non_empty_cells = sum(1 for cell in row_values if cell)

        if non_empty_cells < 4:
            continue

        matching_cols = [col for col in required_columns if col.lower() in map(str.lower, row_values)]
        if len(matching_cols) >= len(required_columns) * threshold:
            return i, row_values

    return None, None


def process_excel_file(file_path):
    """Process the uploaded Excel file and save data to the database with debugging."""
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active

        required_columns = ["Startup ID", "Item Name", "Pipeline", "Location", "Markets",
                            "Founder 1 Name", "Founder 1 Role", "Founder 2 Name", "Founder 2 Role",
                            "Founder 3 Name", "Founder 3 Role", "Founder 4 Name", "Founder 4 Role",
                            "Founder 5 Name", "Founder 5 Role", "Founder 6 Name", "Founder 6 Role",
                            "Founder 7 Name", "Founder 7 Role",
                            "Website 1", "AngelList", "Linkedin", "GitHub", "Twitter", "Facebook", "Google Plus",
                            "Tagline", "Milestone", "Revenue Model", "Source 1 Name", "Source 1 Type", 
                            "Last Contact", "Files", "Incorporated", "Founded", "Differentiators", 
                            "Description", "Interfaces", "Total Funding", "Cash Runway", "Clients", 
                            "Videos", "Rev Last 12 Months", "Rev Last Month", "Rounds"]

        header_row_index, headers = detect_header_row(sheet, required_columns)

        if not header_row_index:
            return False
        
        column_mapping = {col.lower(): i for i, col in enumerate(headers) if col}

        for row in sheet.iter_rows(min_row=header_row_index + 1, values_only=True):
            if not any(row):  
                continue

            startup_id = str(row[column_mapping.get('startup id', '')])
            item_name = str(row[column_mapping.get('item name', '')])
            pipeline = row[column_mapping.get('pipeline', '')]
            location = row[column_mapping.get('location', '')]
            markets = row[column_mapping.get('markets', '')]

            # 🟢 Founders (Stored as JSON)
            founders = []
            for i in range(1, 8):  
                name = row[column_mapping.get(f'founder {i} name'.lower(), '')]
                role = row[column_mapping.get(f'founder {i} role'.lower(), '')]
                if name and role:
                    founders.append({'name': name.strip(), 'role': role.strip()})

            # 🟢 Social Media Links (Stored as JSON)
            social_media = {
                'website': row[column_mapping.get('website 1', '')],
                'angellist': row[column_mapping.get('angellist', '')],
                'linkedin': row[column_mapping.get('linkedin', '')],
                'github': row[column_mapping.get('github', '')],
                'twitter': row[column_mapping.get('twitter', '')],
                'facebook': row[column_mapping.get('facebook', '')],
                'google_plus': row[column_mapping.get('google plus', '')]
            }
            social_media = {k: v.strip() for k, v in social_media.items() if v and v.strip()}

            # 🟢 Other Business Data
            tagline = row[column_mapping.get('tagline', '')]
            milestone = row[column_mapping.get('milestone', '')]
            revenue_model = row[column_mapping.get('revenue model', '')]

            # 🟢 Additional Fields
            last_contact = parse_date(row[column_mapping.get('last contact', '')])
            incorporated = row[column_mapping.get('incorporated', '')]
            founded_date = None  # Default if empty

            if 'founded' in column_mapping:
                raw_founded = row[column_mapping.get('founded', '')]

                if raw_founded:
                    founded_date = parse_date(raw_founded)  # ✅ Convert Month-Year to Date
                else:
                    founded_date = None  # Default to None if empty

            print(f"📅 Founded Date: {founded_date}")  # Debugging
            differentiators = row[column_mapping.get('differentiators', '')]
            description = row[column_mapping.get('description', '')]
            interfaces = row[column_mapping.get('interfaces', '')]

            # 🟢 Financial Data
            total_funding = str(row[column_mapping.get('total funding', '')] or "").strip()
            cash_runway = str(row[column_mapping.get('cash runway', '')] or "").strip()
            rev_last_12_months = str(row[column_mapping.get('rev last 12 months', '')] or "").strip()
            rev_last_month = str(row[column_mapping.get('rev last month', '')] or "").strip()
            rounds = int(row[column_mapping.get('rounds', '')] or 0)  # Keep rounds as an integer
            
            clients = row[column_mapping.get('clients', '')]

            # 🟢 Save to Database
            startup_data = {
                'startup_id': startup_id, 'item_name': item_name, 'pipeline': pipeline,
                'location': location, 'markets': markets, 'founders': founders,
                'social_media': social_media, 'tagline': tagline, 'milestone': milestone,
                'revenue_model': revenue_model, 'last_contact': last_contact,
                'incorporated': incorporated, 'founded_date': founded_date,  # ✅ Added "Founded"
                'differentiators': differentiators, 'description': description,
                'interfaces': interfaces, 'clients': clients,  # ✅ Added "Clients"
                'total_funding': total_funding, 'cash_runway': cash_runway, 
                'rev_last_12_months': rev_last_12_months, 'rev_last_month': rev_last_month, 'rounds': rounds
            }

            startup, created = Startup.objects.update_or_create(
                startup_id=startup_id, defaults=startup_data
            )
            print(f"✅ {'Created' if created else 'Updated'}: {startup.item_name}")

        print("🎉 Processing complete!")
        return True

    except Exception as e:
        print(f"❌ Critical error processing Excel file: {e}")
        return False



def file_upload_success(request):
    return render(request, 'upload_success.html')

def homepage(request):
    return render(request, 'homepage.html')
