from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

from sys import exit


@task
def order_robots_from_Robotsparebin():
    """Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDFR receipt.
    Creates ZIP archive of the receipts and the images."""
    browser.configure(
        slowmo=100,
    )
    open_the_website()
    download_the_csv_file()
    order_robots()
    zip_pdf_receipts()



def open_the_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()


def download_the_csv_file():
    """Downloads the csv file with the orders"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def order_robots():
    """Read data from csv, fill in the order form and saves the receipt"""
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    for order in orders:
        fill_order_form(order)
        export_receipt_as_pdf(order)
        download_robot_image(order)


def fill_order_form(robot):
    page = browser.page()
    page.click("button:text('OK')")
    parts = ["Roll-a-thor head", "Peanut crusher head", "D.A.V.E head", "Andy Roid head", "Spanner mate head", "Drillbit 2000 head"]
    page.select_option("#head", parts[int(robot["Head"]) - 1])
    page.click(f"#id-body-{robot['Body']}")
    page.fill("input.form-control[type='number']", robot["Legs"])
    page.fill("#address", robot["Address"])
    page.click("#preview")
    page.click("#order")


def export_receipt_as_pdf(robot):
    """Exports the receipt to a pdf file"""
    page = browser.page()
    while True:
        try:
            receipt = page.locator("#receipt").inner_html()
            break
        except:
            page.click("#preview")
            page.click("#order")

    pdf = PDF()
    pdf.html_to_pdf(receipt, f"output/receipts/receipt_{robot['Order number']}.pdf")


def download_robot_image(robot):
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path="output/receipts/robot.png")
    list_of_files = [f"output/receipts/receipt_{robot['Order number']}.pdf", "output/receipts/robot.png"]
    page.click("#order-another")

    pdf = PDF()
    pdf.add_files_to_pdf(files=list_of_files, target_document=f"output/receipts/receipt_{robot['Order number']}.pdf")



def zip_pdf_receipts():
    """ZIPs all the pdf receipts"""
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts.zip', recursive=True)


