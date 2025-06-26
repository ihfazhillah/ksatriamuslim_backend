import requests
from datetime import datetime, timezone, timedelta
import re
from decimal import Decimal
from django.conf import settings
from django.core.files.base import ContentFile
from fpdf import FPDF
from .models import (
    UserClockifyConfig,
    Invoice,
    ClockifyTimeEntry,
    ManualInvoiceEntry,
    ClockifyProject,
)
import io


class ClockifyService:
    """Service for integrating with Clockify API"""

    def __init__(self, user_config: UserClockifyConfig):
        self.config = user_config
        self.base_url = "https://api.clockify.me/api/v1"
        self.headers = {
            "X-Api-Key": self.config.api_key,
            "Content-Type": "application/json",
        }
        self.wib_offset = timedelta(hours=7)  # WIB is UTC+7

    def parse_duration(self, duration_str):
        """Parse ISO 8601 duration string to seconds"""
        # Format: PT1H2M3S (1 hour, 2 minutes, 3 seconds)
        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
        match = re.match(pattern, duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def convert_to_wib(self, utc_time_str):
        """Convert UTC time string to WIB"""
        if not utc_time_str:
            return None
        utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
        wib_time = utc_time + self.wib_offset
        return wib_time.replace(tzinfo=timezone(self.wib_offset))

    def get_time_entries(self, start_date, end_date=None):
        """Get time entries from Clockify API with pagination"""
        url = f"{self.base_url}/workspaces/{self.config.workspace_id}/user/{self.config.clockify_user_id}/time-entries"

        # Convert to UTC for API
        if isinstance(start_date, datetime):
            start_utc = (
                start_date.astimezone(timezone.utc)
                if start_date.tzinfo
                else start_date.replace(tzinfo=timezone.utc)
            )
        else:
            start_utc = start_date.replace(tzinfo=timezone.utc)

        if end_date is None:
            # Get current time and add one day to ensure we capture today's data
            end_utc = datetime.now(timezone.utc) + timedelta(days=1)
        else:
            if isinstance(end_date, datetime):
                end_utc = (
                    end_date.astimezone(timezone.utc)
                    if end_date.tzinfo
                    else end_date.replace(tzinfo=timezone.utc)
                )
            else:
                end_utc = end_date.replace(tzinfo=timezone.utc)

        all_entries = []
        page = 1
        page_size = 50  # Maximum allowed by Clockify

        print(f"Fetching time entries from {start_utc} to {end_utc}")

        try:
            while True:
                params = {
                    "start": start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end": end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "page": page,
                    "page-size": page_size,
                }

                print(f"Making request to Clockify API: {url} with params: {params}")
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=30
                )

                print(f"Clockify API response status: {response.status_code}")

                if response.status_code == 200:
                    entries = response.json()
                    print(f"Received {len(entries)} entries on page {page}")

                    if not entries:  # No more entries
                        break

                    all_entries.extend(entries)

                    if len(entries) < page_size:  # Last page
                        break

                    page += 1
                elif response.status_code == 401:
                    raise Exception("Invalid Clockify API key or unauthorized access")
                elif response.status_code == 404:
                    raise Exception("Clockify workspace or user not found")
                else:
                    error_text = response.text
                    print(f"Clockify API error: {response.status_code} - {error_text}")
                    raise Exception(
                        f"Clockify API error ({response.status_code}): {error_text}"
                    )

        except requests.exceptions.Timeout:
            raise Exception("Clockify API request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Unable to connect to Clockify API")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error when accessing Clockify API: {str(e)}")

        print(f"Total entries fetched: {len(all_entries)}")
        return all_entries

    def get_projects(self, force_refresh=False):
        """Get and cache projects from Clockify API"""
        url = f"{self.base_url}/workspaces/{self.config.workspace_id}/projects"

        # Check if we need to refresh cache (older than 24 hours)
        if not force_refresh:
            cache_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            recent_projects = ClockifyProject.objects.filter(
                user=self.config.user, last_synced__gte=cache_cutoff
            )

            if recent_projects.exists():
                print(f"Using cached projects: {recent_projects.count()} projects")
                return {p.clockify_id: p for p in recent_projects}

        print(f"Fetching projects from Clockify API: {url}")

        try:
            all_projects = []
            page = 1
            page_size = 50

            while True:
                params = {
                    "page": page,
                    "page-size": page_size,
                    "archived": "false",  # Only get active projects
                }

                response = requests.get(
                    url, headers=self.headers, params=params, timeout=30
                )

                if response.status_code == 200:
                    projects = response.json()
                    print(f"Received {len(projects)} projects on page {page}")

                    if not projects:  # No more projects
                        break

                    all_projects.extend(projects)

                    if len(projects) < page_size:  # Last page
                        break

                    page += 1
                else:
                    error_text = response.text
                    print(
                        f"Clockify Projects API error: {response.status_code} - {error_text}"
                    )
                    raise Exception(f"Failed to fetch projects: {error_text}")

            # Update cache
            project_cache = {}
            now = datetime.now(timezone.utc)

            for project_data in all_projects:
                project, created = ClockifyProject.objects.update_or_create(
                    user=self.config.user,
                    clockify_id=project_data.get("id", ""),
                    defaults={
                        "name": project_data.get("name", ""),
                        "client_name": project_data.get("clientName", ""),
                        "color": project_data.get("color", ""),
                        "archived": project_data.get("archived", False),
                        "last_synced": now,
                    },
                )
                project_cache[project.clockify_id] = project

                if created:
                    print(f"Cached new project: {project.name}")

            print(f"Total projects cached: {len(project_cache)}")
            return project_cache

        except requests.exceptions.RequestException as e:
            print(f"Network error when fetching projects: {str(e)}")
            # Fall back to existing cache if network fails
            cached_projects = ClockifyProject.objects.filter(user=self.config.user)
            return {p.clockify_id: p for p in cached_projects}

    def get_project_name(self, project_id, project_cache=None):
        """Get project name from cache, fallback to API if needed"""

        if not project_id:
            return "Unknown Project"

        # Use provided cache or get it (less efficient)
        if project_cache is None:
            project_cache = self.get_projects()

        if project_id in project_cache:
            return project_cache[project_id].name

        # If not in cache, try to fetch from API
        try:
            url = f"{self.base_url}/workspaces/{self.config.workspace_id}/projects/{project_id}"
            response = requests.get(url, headers=self.headers, timeout=5)

            if response.status_code == 200:
                project_data = response.json()
                project_name = project_data.get("name", "Unknown Project")

                # Cache this project for future use
                ClockifyProject.objects.update_or_create(
                    user=self.config.user,
                    clockify_id=project_id,
                    defaults={
                        "name": project_name,
                        "client_name": project_data.get("clientName", ""),
                        "color": project_data.get("color", ""),
                        "archived": project_data.get("archived", False),
                        "last_synced": datetime.now(timezone.utc),
                    },
                )

                return project_name
            else:
                print(f"Failed to fetch project {project_id}: {response.status_code}")
                return "Unknown Project"

        except Exception as e:
            print(f"Error fetching project {project_id}: {str(e)}")
            return "Unknown Project"

    def calculate_duration(self, time_entries):
        """Calculate total duration in hours"""
        total_seconds = 0
        for entry in time_entries:
            if entry.get("timeInterval", {}).get("duration"):
                duration_str = entry["timeInterval"]["duration"]
                total_seconds += self.parse_duration(duration_str)

        return Decimal(str(total_seconds / 3600))  # Convert to hours

    def process_time_entries_for_invoice(self, invoice: Invoice, time_entries):
        """Process and save time entries for an invoice"""
        processed_entries = []

        # Get project cache ONCE for all entries - PERFORMANCE OPTIMIZATION
        project_cache = self.get_projects()

        for entry in time_entries:
            time_interval = entry.get("timeInterval", {})
            duration_str = time_interval.get("duration", "PT0S")
            duration_hours = Decimal(str(self.parse_duration(duration_str) / 3600))

            start_time = self.convert_to_wib(time_interval.get("start", ""))
            end_time = self.convert_to_wib(time_interval.get("end", ""))

            # Get project information
            project_data = entry.get("project", {})
            project_id = project_data.get("id", "")

            # Resolve project name from cache
            project_name = ""
            if project_id and project_id in project_cache:
                cached_project = project_cache[project_id]
                project_name = cached_project.name
                print(f"Resolved project {project_id} -> {project_name}")
            elif project_data.get("name"):
                # Fallback to direct name from API if available
                project_name = project_data.get("name", "")
                print(f"Using direct project name: {project_name}")
            else:
                project_name = "Unknown Project"
                print(f"Could not resolve project for ID: {project_id}")

            time_entry, created = ClockifyTimeEntry.objects.get_or_create(
                invoice=invoice,
                clockify_id=entry.get("id", ""),
                defaults={
                    "description": entry.get("description", ""),
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_hours": duration_hours,
                    "project_id": project_id,
                    "project_name": project_name,
                    "task_name": entry.get("task", {}).get("name", ""),
                },
            )

            processed_entries.append(time_entry)

        return processed_entries

    def sync_projects(self, force_refresh=True):
        """Manually sync projects - useful for testing and initial setup"""
        print("Starting manual project sync...")
        project_cache = self.get_projects(force_refresh=force_refresh)

        print(f"Synced {len(project_cache)} projects:")
        for project_id, project in project_cache.items():
            print(f"  - {project.name} (ID: {project_id})")

        return project_cache

    def test_connection_and_sync(self):
        """Test connection and sync projects"""
        try:
            # Test basic connection
            url = f"{self.base_url}/workspaces/{self.config.workspace_id}/projects"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API connection failed: {response.status_code}",
                }

            # Sync projects
            project_cache = self.sync_projects(force_refresh=True)

            return {
                "success": True,
                "message": f"Connected successfully. Synced {len(project_cache)} projects.",
                "projects": [
                    {"id": p.clockify_id, "name": p.name}
                    for p in project_cache.values()
                ],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class ModernInvoicePDF(FPDF):
    """Modern PDF class for invoice generation"""

    def __init__(self, user_config: UserClockifyConfig):
        super().__init__()
        self.config = user_config

    def header(self):
        # Sender info with modern styling
        self.set_font("Arial", "B", 10)
        self.set_text_color(44, 62, 80)  # Dark blue-gray
        self.cell(0, 6, self.config.company_name, 0, 1, "R")

        self.set_font("Arial", "", 8)
        self.set_text_color(52, 73, 94)  # Lighter blue-gray
        self.cell(0, 5, self.config.company_address_line1, 0, 1, "R")
        self.cell(0, 5, self.config.company_address_line2, 0, 1, "R")
        self.cell(0, 5, self.config.company_address_line3, 0, 1, "R")
        self.cell(0, 5, self.config.company_address_line4, 0, 1, "R")

        # Line break
        self.ln(10)

        # Draw top line
        self.set_draw_color(41, 128, 185)  # Blue
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(4)

        # Invoice title with modern styling
        self.set_font("Arial", "B", 18)
        self.set_text_color(41, 128, 185)  # Blue
        self.cell(0, 10, "INVOICE", 0, 1, "C")

        # Draw bottom line
        self.ln(4)
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(5)

        # Reset text color
        self.set_text_color(0, 0, 0)


class InvoiceGeneratorService:
    """Service for generating invoice PDFs"""

    def __init__(self, user_config: UserClockifyConfig):
        self.config = user_config

    def generate_invoice_pdf(self, invoice: Invoice) -> bytes:
        """Generate PDF for an invoice and return as bytes"""
        pdf = ModernInvoicePDF(self.config)
        pdf.add_page()

        # Invoice details
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(0, 10, f"Invoice Number: {invoice.invoice_number}", 0, 1, "R")
        pdf.cell(0, 10, f"Date: {invoice.invoice_date.strftime('%Y-%m-%d')}", 0, 1, "R")

        # Bill to
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 10, "Bill To:", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(0, 10, invoice.client.name, 0, 1)

        if invoice.client.address_line1:
            pdf.cell(0, 10, invoice.client.address_line1, 0, 1)
        if invoice.client.address_line2:
            pdf.cell(0, 10, invoice.client.address_line2, 0, 1)
        if invoice.client.address_line3:
            pdf.cell(0, 10, invoice.client.address_line3, 0, 1)
        if invoice.client.address_line4:
            pdf.cell(0, 10, invoice.client.address_line4, 0, 1)

        # Table header
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(41, 128, 185)
        headers = ["Description", "Rate (USD)", "Quantity", "Total (USD)"]
        col_widths = [80, 40, 40, 30]

        # Draw header background
        pdf.set_fill_color(236, 240, 241)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, "C", True)
        pdf.ln()

        # Table content
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(44, 62, 80)

        # Group time entries by project
        time_entries = invoice.time_entries.all()
        project_groups = {}

        # Calculate hours per project
        for entry in time_entries:
            project_name = entry.project_name or "Unknown Project"
            if project_name not in project_groups:
                project_groups[project_name] = 0
            project_groups[project_name] += float(entry.duration_hours)

        # Calculate hourly rate
        hourly_rate = float(invoice.hourly_rate)

        # Add line for each project
        for project_name, project_hours in project_groups.items():
            project_desc = f"{project_name} [{invoice.period_start.strftime('%Y-%m-%d')} - {invoice.period_end.strftime('%Y-%m-%d')}]"
            project_total = project_hours * hourly_rate

            pdf.cell(col_widths[0], 10, project_desc, 1, 0)
            pdf.cell(col_widths[1], 10, f"${hourly_rate:.2f}", 1, 0, "R")
            pdf.cell(col_widths[2], 10, f"{project_hours:.2f}h", 1, 0, "R")
            pdf.cell(col_widths[3], 10, f"${project_total:.2f}", 1, 1, "R")

        # Add manual entries
        for entry in invoice.manual_entries.all():
            pdf.cell(col_widths[0], 10, entry.description[:40], 1, 0)
            pdf.cell(col_widths[1], 10, f"${entry.rate}", 1, 0, "R")
            pdf.cell(col_widths[2], 10, f"{entry.quantity}", 1, 0, "R")
            pdf.cell(col_widths[3], 10, f"${entry.total_amount}", 1, 1, "R")

        # Totals
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(41, 128, 185)

        pdf.set_fill_color(236, 240, 241)
        pdf.cell(
            0, 10, f"Exchange Rate: Rp {invoice.conversion_rate:,}", 0, 1, "R", True
        )
        pdf.cell(0, 10, f"Total (USD): ${invoice.subtotal_usd:.2f}", 0, 1, "R", True)
        pdf.cell(0, 10, f"Total (IDR): Rp {invoice.total_idr:,.2f}", 0, 1, "R", True)

        # Payment Note
        pdf.ln(20)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 10, "Payment Information:", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(0, 10, self.config.payment_info_line1, 0, 1)
        pdf.cell(0, 10, self.config.payment_info_line2, 0, 1)

        # Return PDF as bytes
        pdf_output = pdf.output(dest="S")
        return (
            pdf_output
            if isinstance(pdf_output, bytes)
            else pdf_output.encode("latin-1")
        )

    def save_invoice_pdf(self, invoice: Invoice) -> str:
        """Generate and save PDF file for an invoice"""
        pdf_bytes = self.generate_invoice_pdf(invoice)

        # Save to file field
        filename = f"invoice_{invoice.invoice_number}.pdf"
        invoice.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

        return filename


class InvoiceService:
    """Service for invoice business logic"""

    @staticmethod
    def create_invoice_from_clockify(
        user,
        client,
        invoice_number,
        invoice_date,
        period_start,
        period_end,
        tax_rate=0,
        conversion_rate=None,
        excluded_entries=None,
        manual_entries=None,
    ):
        """Create invoice from Clockify time entries"""
        try:
            user_config = user.clockify_config
        except UserClockifyConfig.DoesNotExist:
            raise ValueError("User Clockify configuration not found")

        # Get Clockify time entries
        clockify_service = ClockifyService(user_config)
        time_entries = clockify_service.get_time_entries(period_start, period_end)

        # Filter out excluded entries
        if excluded_entries:
            time_entries = [
                entry
                for entry in time_entries
                if entry.get("id") not in excluded_entries
            ]

        total_hours = clockify_service.calculate_duration(time_entries)

        # Use provided conversion rate or fall back to user config
        final_conversion_rate = conversion_rate or user_config.conversion_rate

        # Create invoice
        invoice = Invoice.objects.create(
            user=user,
            client=client,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            period_start=period_start,
            period_end=period_end,
            total_hours=total_hours,
            hourly_rate=user_config.hourly_rate,
            conversion_rate=final_conversion_rate,
        )

        # Process and save time entries
        clockify_service.process_time_entries_for_invoice(invoice, time_entries)

        # Add manual entries if provided
        if manual_entries:
            for entry_data in manual_entries:
                ManualInvoiceEntry.objects.create(
                    invoice=invoice,
                    description=entry_data["description"],
                    rate=Decimal(str(entry_data["rate"])),
                    quantity=Decimal(str(entry_data["quantity"])),
                )

        # Calculate totals
        invoice.calculate_totals()
        invoice.save()

        # Generate PDF
        pdf_service = InvoiceGeneratorService(user_config)
        pdf_service.save_invoice_pdf(invoice)

        return invoice
