import pysftp
import os
import database
import xml.etree.ElementTree as ET
import datetime
from email.message import EmailMessage
import smtplib

class Sftp:
    def __init__(self, hostname, username, password, port=22):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        try:
            # Get the sftp connection object
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                cnopts=cnopts
            )
        except Exception as err:
            raise Exception(err)
        finally:
            print(f"Connected to {self.hostname} as {self.username}.")

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close() # type: ignore
        print(f"Disconnected from host {self.hostname}")

    def listdir(self, remote_path):
        """lists all the files and directories in the specified path and returns them"""
        for obj in self.connection.listdir(remote_path): # type: ignore
            yield obj
        self.disconnect()

    def listdir_attr(self, remote_path):
        """lists all the files and directories (with their attributes) in the specified path and returns them"""
        for attr in self.connection.listdir_attr(remote_path): # type: ignore
            yield attr

    def download(self, remote_path, target_local_path):
        """
        Downloads the file from remote sftp server to local.
        Also, by default extracts the file to the specified target_local_path
        """
        try:
            print(
                f"downloading from {self.hostname} as {self.username} [(remote path : {remote_path});(local path: {target_local_path})]"
            )
            # Download from remote sftp server to local
            self.connection.get(remote_path, target_local_path) # type: ignore
            print("download completed")

        except Exception as err:
            raise Exception(err)      
        #self.disconnect()
    def upload(self, source_local_path, remote_path):
        """
        Uploads the source files from local to the sftp server.
        """
        try:
            print(
                f"uploading to {self.hostname} as {self.username} [(remote path: {remote_path});(source local path: {source_local_path})]"
            )
            # Download file from SFTP
            self.connection.put(source_local_path, remote_path) # type: ignore
            print("upload completed")
        except Exception as err:
            raise Exception(err)
 
def extract_values_from_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    numbl_values = [elem.text for elem in root.findall('.//NUMBL')]
    numorder_values = [elem.text for elem in root.findall('.//NUMORDER')]
    #print(numorder_values)
    return numbl_values[0][2:], numorder_values[0] # type: ignore

def posliNaMail(mail: str, file: str, gw_number):
    nazev_kont = file.split('/')[-1]
    msg = EmailMessage()
    msg['Subject'] = f'Invio POD, GW_number {gw_number}'
    msg['From'] = 'gwsyrovice@seznam.cz'
    msg['To'] = mail
    msg.set_content(
        f'Automaticky vygenerovany mail.\nNahravani POD Invio...\n\nTestovaci provoz.\n')
    with open(file, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application',
                           subtype='pdf', filename=nazev_kont)
    with smtplib.SMTP_SSL('smtp.seznam.cz', 465) as server:
        server = smtplib.SMTP_SSL('smtp.seznam.cz', 465)
        server.login('gwsyrovice@seznam.cz', 'tajneheslo111')
        server.send_message(msg)
        

if __name__ == "__main__":
    sftp = Sftp(hostname = "flux.inviologistics.com", username = "gw-world", password = "aAELDkBwHbya", port = 48769, )
    # Connect to SFTP
    sftp.connect()
    # Stazeni vsech XML v EXTRA
    print(f"Stazeni xml souboru v /EXTRA/ adresari:")
    seznam_uz_nahranych=database.select_filenames()
    for file in sftp.listdir_attr("/EXTRA/"):
        if file.filename.endswith('.xml') and file.filename not in seznam_uz_nahranych:
            sftp.download("EXTRA/"+file.filename, "locdir/"+file.filename)
            gw_numbers, invio_numbers = extract_values_from_xml("locdir/"+file.filename)
            values = (datetime.date.today(),file.filename, gw_numbers, invio_numbers,  False)
            database.insert_item(values)
            if os.path.exists("locdir/"+file.filename):
                os.remove("locdir/"+file.filename)
   
    seznam_neposlanych = database.select_neposlane()
    
    print(f"Seznam neposlanych POD, invio cisla:\n {seznam_neposlanych}")
    for file in sftp.listdir_attr("/POD/"):
        if file.filename.endswith('.pdf'):
            invio_number = file.filename.split('.')[0][2:]
            gw_number = database.select_gw_number(invio_number=invio_number)
            if file.filename.split(".")[0][2:] in seznam_neposlanych:
                print(f"Soubor {file.filename} prejmenovan dle GW pozice: {gw_number}")
                sftp.download("/POD/"+file.filename, "locdir/"+gw_number+".pdf")
                posliNaMail("mirekczk@gmail.com", "locdir/"+gw_number+".pdf", gw_number=gw_number )
                posliNaMail("viktor.nemecek@gw-world.com", "locdir/"+gw_number+".pdf", gw_number=gw_number )
                if os.path.exists(f"locdir/"+gw_number+".pdf"):
                    os.remove(f"locdir/"+gw_number+".pdf")
                database.update_item(invio_number=invio_number, set_sent_by_email=True)
            else:
                print(f"Soubor {file.filename} - POD uz nahrano, GW pozice: {gw_number}")
    