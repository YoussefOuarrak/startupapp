import openpyxl
import json
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileUploadForm
from .models import Startup, UploadedFile, StartupApplication
from datetime import datetime

logger = logging.getLogger(__name__)

import re
from datetime import datetime


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()

            try:
                wb = openpyxl.load_workbook(uploaded_file.file.path, data_only=True)
                sheet = wb.active

                # 🔍 Dynamically detect header row
                required_columns = ["Application ID"]
                header_row_idx, detected_headers = detect_header_row(sheet, required_columns)

                if header_row_idx is None:
                    print("❌ Could not detect a valid header row")
                    messages.error(request, "Could not detect a valid header row in the file.")
                    return redirect('file_upload_success')

                print(f"📌 Detected header row: {detected_headers}")

                # 🔥 Detect file type dynamically
                if "application id" in [h.lower() for h in detected_headers]:  
                    print("🔍 PVA file format detected based on detected headers")
                    success = process_pva_file(uploaded_file.file.path)
                else:
                    print("🔍 Pipeline file format assumed")
                    success = process_excel_file(uploaded_file.file.path)

                if success:
                    uploaded_file.processed = True
                    uploaded_file.save()
                    messages.success(request, "File uploaded and processed successfully! ✅")
                else:
                    messages.error(request, "File processing failed. Please check the format.")

            except Exception as e:
                print(f"❌ Error in upload_file: {str(e)}")
                messages.error(request, f"Error reading file: {e}")

            return redirect('file_upload_success')

    else:
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form})


def process_pva_file(file_path):
    """Process the uploaded PVA file and store applications separately."""
    try:
        print("🔍 Starting PVA file processing")
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active

        # Find the header row - directly search for Application ID
        header_row_idx = None
        headers = []

        # Search through first 10 rows to find the header
        for i in range(1, 10):
            row_values = [str(cell.value).strip() if cell.value else "" for cell in sheet[i]]
            if "Application ID" in row_values:
                header_row_idx = i
                headers = row_values
                print(f"📌 Found header row at index {i}: {headers}")
                break

        if not header_row_idx:
            print("❌ Could not find a row containing 'Application ID'")
            return False

        # Ensure headers are correctly extracted
        print(f"✅ Extracted Headers: {headers}")

        # Create column indices mapping (column name -> index)
        column_indices = {}
        for col_index, header in enumerate(headers):
            if header:  # Skip empty headers
                column_indices[header.lower()] = col_index

        print(f"📌 Column indices mapping created: {column_indices}")

        # Verify essential columns exist
        required_columns = ['application id', 'startup/person name']
        missing_columns = [col for col in required_columns if col not in column_indices]

        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False

        # Process data rows
        data_start_row = header_row_idx + 1
        row_count = 0
        success_count = 0

        # Ensure safe access to values
        def safe_get_value(idx, row_data):
            """ Ensure idx is a valid integer before accessing row_data """
            if idx is None or not isinstance(idx, int) or idx >= len(row_data):
                return None
            val = row_data[idx]
            return str(val).strip() if val is not None else None

        for row_idx in range(data_start_row, sheet.max_row + 1):
            # Ensure row_data is a list
            row_data = [cell.value for cell in sheet[row_idx]]  

            # Debugging: Print each row before processing
            print(f"🔍 Row {row_idx}: {row_data}")

            # Skip empty rows
            if not any(row_data):
                continue

            row_count += 1

            try:
                # Extract values using column indices
                application_id = safe_get_value(column_indices.get('application id'), row_data)  # IDs should remain as is
                startup_name = safe_get_value(column_indices.get('startup/person name'), row_data)  # IDs should remain as is

                applicant_name = safe_get_value(column_indices.get('primary contact name'), row_data) or ""
                email = safe_get_value(column_indices.get('primary contact email address'), row_data) or ""
                phone = safe_get_value(column_indices.get('primary contact title'), row_data) or ""
                pitch = safe_get_value(column_indices.get('brief description'), row_data) or ""
                funding_requested = safe_get_value(column_indices.get('amount raising'), row_data) or ""
                business_stage = safe_get_value(column_indices.get('fund stage'), row_data) or ""

                # Debug extracted values
                print(f"✅ Extracted Data - App ID: {application_id}, Name: {startup_name}")

                # Skip if essential data is missing
                if not application_id or not startup_name:
                    print(f"⚠️ Skipping row {row_idx}: Missing application ID or startup name")
                    continue

                # Link to existing startup
                startup = Startup.objects.filter(item_name__icontains=startup_name).first()
                if not startup:
                    print(f"⚠️ No matching startup found for '{startup_name}'")
                    continue

                # Create or update the application
                application, created = StartupApplication.objects.update_or_create(
                    application_id=application_id,
                    defaults={
                        'startup': startup,
                        'applicant_name': applicant_name,
                        'email': email,
                        'phone': phone,
                        'pitch': pitch,
                        'funding_requested': funding_requested,
                        'business_stage': business_stage,
                    }
)

                print(f"✅ {'Created' if created else 'Updated'} application: {application_id}")
                success_count += 1

            except Exception as e:
                print(f"❌ Error processing row {row_idx}: {str(e)}")
                import traceback
                traceback.print_exc()

        print(f"🎉 PVA processing complete! Processed {row_count} rows, {success_count} successful.")
        return success_count > 0

    except Exception as e:
        print(f"❌ Critical error processing PVA file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


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

def detect_header_row(sheet, required_columns, pva_columns=None, threshold=0.4):
    """Dynamically detect the header row based on required column names for both Pipeline & PVA."""
    for i, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        row_values = [str(cell).strip() if cell else "" for cell in row]
        non_empty_cells = sum(1 for cell in row_values if cell)

        if non_empty_cells < 4:  # Ignore empty rows
            continue

        # 🔥 Check if it matches Pipeline headers
        matching_pipeline_cols = [col for col in required_columns if col.lower() in map(str.lower, row_values)]
        
        # 🔥 Check if it matches PVA headers
        matching_pva_cols = [col for col in (pva_columns or []) if col.lower() in map(str.lower, row_values)]

        if len(matching_pipeline_cols) >= len(required_columns) * threshold:
            print(f"📌 Detected Pipeline header row at index {i}: {row_values}")  # Debugging
            return i, row_values  # ✅ Pipeline detected

        if len(matching_pva_cols) >= len((pva_columns or [])) * threshold:
            print(f"📌 Detected PVA header row at index {i}: {row_values}")  # Debugging
            return i, row_values  # ✅ PVA detected

    return None, None  # ❌ No valid header row found

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


