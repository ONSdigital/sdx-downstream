from app import settings
import zipfile
import io
from ftplib import FTP


def get_ftp_folder(survey):
    if 'heartbeat' in survey and survey['heartbeat'] is True:
        return settings.FTP_HEARTBEAT_FOLDER
    else:
        return settings.FTP_FOLDER


def connect_to_ftp():
    ftp = FTP(settings.FTP_HOST)
    ftp.login(user=settings.FTP_USER, passwd=settings.FTP_PASS)
    return ftp


def process_zip_to_ftp(logger, folder, zip_contents):
    try:
        z = zipfile.ZipFile(io.BytesIO(zip_contents))
        logger.debug("Unzipped contents", filelist=z.namelist())

        ftp = connect_to_ftp()
        for filename in z.namelist():
            if filename.endswith('/'):
                continue

            logger.debug("Processing file to FTP", folder=folder, filename=filename)
            edc_file = z.open(filename)
            deliver_binary_to_ftp(ftp, folder, filename, edc_file.read())

        ftp.quit()
        return True

    except (RuntimeError, zipfile.BadZipfile) as e:
        logger.error("Bad zip file", exception=e)
        return False


def deliver_binary_to_ftp(ftp, folder, filename, data):
    stream = io.BytesIO(data)
    ftp.cwd(folder)
    ftp.storbinary('STOR ' + filename, stream)
